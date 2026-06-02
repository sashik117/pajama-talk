import type { CallSummaryDto } from "../api";
import type { MoodKey } from "../state/chatState";
import type { AudioPayload } from "../utils/audio";

export type SpeakingTransport = "text" | "voice";
export type VoiceAudioChunk = {
  audioBase64: string;
  mimeType?: string;
  transcript?: string;
};

type SpeakingTokenEvent = {
  type: "token" | "assistant_token";
  value?: string;
};

type SpeakingServerEvent =
  | SpeakingTokenEvent
  | { type: "assistant_text"; value?: string }
  | { type: "tts"; text?: string; speed?: number; provider?: string; audio_base64?: string | null; mime_type?: string | null }
  | { type: "transcript"; value?: string; provider?: string; confidence?: number }
  | { type: "stt_status"; value?: string; chunks?: number; bytes?: number; provider?: string }
  | { type: "session_ready"; stt?: string; tts?: string; capabilities?: Record<string, unknown> }
  | { type: "call_summary"; value?: CallSummaryDto }
  | { type: "pong" }
  | { type: "error"; value?: string }
  | { type: "done" };

type SpeakingUrlBuilder = (path: string) => string;
type RealtimeGuardOptions = {
  heartbeatMs?: number;
  timeoutMs?: number;
  retries?: number;
};

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

function turnResult(finalReply: string, audio?: AudioPayload): { finalReply: string; audio?: AudioPayload } {
  return audio ? { finalReply, audio } : { finalReply };
}

function voiceAudioResult(
  finalReply: string,
  transcript: string,
  audio?: AudioPayload
): { finalReply: string; transcript: string; audio?: AudioPayload } {
  return audio ? { finalReply, transcript, audio } : { finalReply, transcript };
}

export async function sendSpeakingTurn({
  wsUrl,
  token,
  roomId,
  mood,
  message,
  speechRate,
  transport,
  onToken,
  heartbeatMs = 15000,
  timeoutMs = 45000,
  retries = 0
}: {
  wsUrl: SpeakingUrlBuilder;
  token: string;
  roomId: string;
  mood: MoodKey;
  message: string;
  speechRate: number;
  transport: SpeakingTransport;
  onToken: (reply: string, event: SpeakingTokenEvent) => void;
} & RealtimeGuardOptions): Promise<{ finalReply: string; audio?: AudioPayload }> {
  try {
    return await openSpeakingTurn({
      wsUrl,
      token,
      roomId,
      mood,
      message,
      speechRate,
      transport,
      onToken,
      heartbeatMs,
      timeoutMs
    });
  } catch (err) {
    if (retries <= 0) throw err;
    return openSpeakingTurn({
      wsUrl,
      token,
      roomId,
      mood,
      message,
      speechRate,
      transport,
      onToken,
      heartbeatMs,
      timeoutMs
    });
  }
}

async function openSpeakingTurn({
  wsUrl,
  token,
  roomId,
  mood,
  message,
  speechRate,
  transport,
  onToken,
  heartbeatMs,
  timeoutMs
}: {
  wsUrl: SpeakingUrlBuilder;
  token: string;
  roomId: string;
  mood: MoodKey;
  message: string;
  speechRate: number;
  transport: SpeakingTransport;
  onToken: (reply: string, event: SpeakingTokenEvent) => void;
  heartbeatMs: number;
  timeoutMs: number;
}): Promise<{ finalReply: string; audio?: AudioPayload }> {
  return new Promise((resolve, reject) => {
    const socket = new WebSocket(wsUrl(speakingPath({ token, roomId, mood, transport })));
    let streamedReply = "";
    let finalReply = "";
    let audio: AudioPayload | undefined;
    let settled = false;
    let heartbeatTimer: ReturnType<typeof setInterval> | undefined;
    const timeoutTimer = setTimeout(() => {
      socket.close();
      settle(() => reject(new Error("Speaking stream timed out.")));
    }, timeoutMs);

    const cleanup = () => {
      clearTimeout(timeoutTimer);
      if (heartbeatTimer) clearInterval(heartbeatTimer);
    };

    const settle = (handler: () => void) => {
      if (settled) return;
      settled = true;
      cleanup();
      handler();
    };

    socket.onopen = () => {
      heartbeatTimer = setInterval(() => {
        if (socket.readyState === WebSocket.OPEN) socket.send(JSON.stringify({ type: "ping" }));
      }, heartbeatMs);
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
          if (payload.audio_base64 && payload.mime_type) {
            audio = { audioBase64: payload.audio_base64, mimeType: payload.mime_type };
          }
          break;
        case "pong":
          break;
        case "error":
          socket.close();
          settle(() => reject(new Error(payload.value || "Speaking stream failed.")));
          break;
        case "done":
          socket.close();
          settle(() => resolve(turnResult(finalReply.trim(), audio)));
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
  roomId,
  heartbeatMs = 15000,
  timeoutMs = 30000
}: {
  wsUrl: SpeakingUrlBuilder;
  token: string;
  roomId: string;
} & RealtimeGuardOptions): Promise<CallSummaryDto> {
  return new Promise((resolve, reject) => {
    const params = new URLSearchParams({ token, room_id: roomId });
    const socket = new WebSocket(wsUrl(`/speaking/voice-ws?${params.toString()}`));
    let settled = false;
    let heartbeatTimer: ReturnType<typeof setInterval> | undefined;
    const timeoutTimer = setTimeout(() => {
      socket.close();
      settle(() => reject(new Error("Call summary timed out.")));
    }, timeoutMs);

    const cleanup = () => {
      clearTimeout(timeoutTimer);
      if (heartbeatTimer) clearInterval(heartbeatTimer);
    };

    const settle = (handler: () => void) => {
      if (settled) return;
      settled = true;
      cleanup();
      handler();
    };

    socket.onopen = () => {
      heartbeatTimer = setInterval(() => {
        if (socket.readyState === WebSocket.OPEN) socket.send(JSON.stringify({ type: "ping" }));
      }, heartbeatMs);
      socket.send(JSON.stringify({ type: "end_call" }));
    };
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

export async function sendVoiceAudioTurn({
  wsUrl,
  token,
  roomId,
  mood,
  chunks,
  transcriptHint,
  speechRate,
  onToken,
  onStatus,
  heartbeatMs = 15000,
  timeoutMs = 45000,
  retries = 0
}: {
  wsUrl: SpeakingUrlBuilder;
  token: string;
  roomId: string;
  mood: MoodKey;
  chunks: VoiceAudioChunk[];
  transcriptHint?: string;
  speechRate: number;
  onToken: (reply: string, event: SpeakingTokenEvent) => void;
  onStatus?: (event: SpeakingServerEvent) => void;
} & RealtimeGuardOptions): Promise<{ finalReply: string; transcript: string; audio?: AudioPayload }> {
  try {
    return await openVoiceAudioTurn({
      wsUrl,
      token,
      roomId,
      mood,
      chunks,
      transcriptHint,
      speechRate,
      onToken,
      onStatus,
      heartbeatMs,
      timeoutMs
    });
  } catch (err) {
    if (retries <= 0) throw err;
    return openVoiceAudioTurn({
      wsUrl,
      token,
      roomId,
      mood,
      chunks,
      transcriptHint,
      speechRate,
      onToken,
      onStatus,
      heartbeatMs,
      timeoutMs
    });
  }
}

async function openVoiceAudioTurn({
  wsUrl,
  token,
  roomId,
  mood,
  chunks,
  transcriptHint,
  speechRate,
  onToken,
  onStatus,
  heartbeatMs,
  timeoutMs
}: {
  wsUrl: SpeakingUrlBuilder;
  token: string;
  roomId: string;
  mood: MoodKey;
  chunks: VoiceAudioChunk[];
  transcriptHint?: string;
  speechRate: number;
  onToken: (reply: string, event: SpeakingTokenEvent) => void;
  onStatus?: (event: SpeakingServerEvent) => void;
  heartbeatMs: number;
  timeoutMs: number;
}): Promise<{ finalReply: string; transcript: string; audio?: AudioPayload }> {
  return new Promise((resolve, reject) => {
    const socket = new WebSocket(wsUrl(speakingPath({ token, roomId, mood, transport: "voice" })));
    let streamedReply = "";
    let finalReply = "";
    let transcript = "";
    let audio: AudioPayload | undefined;
    let settled = false;
    let heartbeatTimer: ReturnType<typeof setInterval> | undefined;
    const timeoutTimer = setTimeout(() => {
      socket.close();
      settle(() => reject(new Error("Voice audio stream timed out.")));
    }, timeoutMs);

    const cleanup = () => {
      clearTimeout(timeoutTimer);
      if (heartbeatTimer) clearInterval(heartbeatTimer);
    };

    const settle = (handler: () => void) => {
      if (settled) return;
      settled = true;
      cleanup();
      handler();
    };

    socket.onopen = () => {
      heartbeatTimer = setInterval(() => {
        if (socket.readyState === WebSocket.OPEN) socket.send(JSON.stringify({ type: "ping" }));
      }, heartbeatMs);
    };

    socket.onerror = () => settle(() => reject(new Error("Voice audio stream failed.")));

    socket.onmessage = (event) => {
      const payload = parseSpeakingEvent(String(event.data));
      switch (payload.type) {
        case "session_ready":
          chunks.forEach((chunk) => {
            socket.send(JSON.stringify({
              type: "audio_chunk",
              audio_base64: chunk.audioBase64,
              mime_type: chunk.mimeType,
              transcript: chunk.transcript
            }));
          });
          socket.send(JSON.stringify({ type: "end_audio", transcript: transcriptHint, speed: speechRate }));
          onStatus?.(payload);
          break;
        case "stt_status":
          onStatus?.(payload);
          break;
        case "transcript":
          transcript = payload.value ?? "";
          onStatus?.(payload);
          break;
        case "assistant_token":
        case "token":
          streamedReply += payload.value ?? "";
          finalReply = streamedReply.trim();
          onToken(streamedReply.trimStart(), payload);
          break;
        case "tts":
          if (payload.text) finalReply = payload.text;
          if (payload.audio_base64 && payload.mime_type) {
            audio = { audioBase64: payload.audio_base64, mimeType: payload.mime_type };
          }
          onStatus?.(payload);
          break;
        case "pong":
          break;
        case "error":
          socket.close();
          settle(() => reject(new Error(payload.value || "Voice audio stream failed.")));
          break;
        case "done":
          socket.close();
          settle(() => resolve(voiceAudioResult(finalReply.trim(), transcript, audio)));
          break;
        default:
          break;
      }
    };
  });
}
