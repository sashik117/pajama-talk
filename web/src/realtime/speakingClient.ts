import type { CallSummaryDto } from "../api";
import type { MoodKey } from "../state/chatState";

export type SpeakingTransport = "text" | "voice";

type SpeakingTokenEvent = {
  type: "token" | "assistant_token";
  value?: string;
};

type SpeakingServerEvent =
  | SpeakingTokenEvent
  | { type: "assistant_text"; value?: string }
  | { type: "tts"; text?: string; speed?: number }
  | { type: "transcript"; value?: string }
  | { type: "stt_status"; value?: string }
  | { type: "session_ready"; stt?: string; tts?: string }
  | { type: "call_summary"; value?: CallSummaryDto }
  | { type: "error"; value?: string }
  | { type: "done" };

type SpeakingUrlBuilder = (path: string) => string;

function parseSpeakingEvent(raw: string): SpeakingServerEvent {
  try {
    const payload = JSON.parse(raw) as SpeakingServerEvent;
    return payload?.type ? payload : { type: "error", value: "Malformed realtime event." };
  } catch {
    return { type: "error", value: "Malformed realtime event." };
  }
}

function speakingPath(input: {
  token: string;
  roomId: string;
  mood?: MoodKey;
  transport: SpeakingTransport;
}) {
  const channel = input.transport === "voice" ? "voice-ws" : "ws";
  const params = new URLSearchParams({
    token: input.token,
    room_id: input.roomId,
    mood: input.mood ?? "steady"
  });
  return `/speaking/${channel}?${params.toString()}`;
}

export async function sendSpeakingTurn({
  wsUrl,
  token,
  roomId,
  mood,
  message,
  speechRate,
  transport,
  onToken
}: {
  wsUrl: SpeakingUrlBuilder;
  token: string;
  roomId: string;
  mood: MoodKey;
  message: string;
  speechRate: number;
  transport: SpeakingTransport;
  onToken: (reply: string, event: SpeakingTokenEvent) => void;
}): Promise<{ finalReply: string }> {
  return new Promise((resolve, reject) => {
    const socket = new WebSocket(wsUrl(speakingPath({ token, roomId, mood, transport })));
    let streamedReply = "";
    let finalReply = "";
    let settled = false;

    const settle = (handler: () => void) => {
      if (settled) return;
      settled = true;
      handler();
    };

    socket.onopen = () => {
      if (transport === "voice") {
        socket.send(JSON.stringify({ type: "user_text", value: message, speed: speechRate }));
      } else {
        socket.send(message);
      }
    };

    socket.onerror = () => {
      settle(() => reject(new Error("WebSocket failed.")));
    };

    socket.onmessage = (event) => {
      const payload = parseSpeakingEvent(String(event.data));
      switch (payload.type) {
        case "token":
        case "assistant_token":
          streamedReply += payload.value ?? "";
          finalReply = streamedReply.trim();
          onToken(streamedReply.trimStart(), payload);
          break;
        case "assistant_text":
          if (payload.value) finalReply = payload.value;
          break;
        case "tts":
          if (payload.text) finalReply = payload.text;
          break;
        case "error":
          socket.close();
          settle(() => reject(new Error(payload.value || "Speaking stream failed.")));
          break;
        case "done":
          socket.close();
          settle(() => resolve({ finalReply: finalReply.trim() }));
          break;
        default:
          break;
      }
    };
  });
}

export async function requestCallSummary({
  wsUrl,
  token,
  roomId
}: {
  wsUrl: SpeakingUrlBuilder;
  token: string;
  roomId: string;
}): Promise<CallSummaryDto> {
  return new Promise((resolve, reject) => {
    const params = new URLSearchParams({ token, room_id: roomId });
    const socket = new WebSocket(wsUrl(`/speaking/voice-ws?${params.toString()}`));
    let settled = false;

    const settle = (handler: () => void) => {
      if (settled) return;
      settled = true;
      handler();
    };

    socket.onopen = () => socket.send(JSON.stringify({ type: "end_call" }));
    socket.onerror = () => settle(() => reject(new Error("Call summary failed.")));
    socket.onmessage = (event) => {
      const payload = parseSpeakingEvent(String(event.data));
      if (payload.type === "call_summary" && payload.value) {
        socket.close();
        settle(() => resolve(payload.value as CallSummaryDto));
      }
      if (payload.type === "error") {
        socket.close();
        settle(() => reject(new Error(payload.value || "Call summary failed.")));
      }
    };
  });
}
