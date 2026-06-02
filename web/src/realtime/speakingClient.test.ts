import { beforeEach, describe, expect, it, vi } from "vitest";
import { requestCallSummary, sendSpeakingTurn, sendVoiceAudioTurn } from "./speakingClient";

class FakeWebSocket {
  static OPEN = 1;
  static instances: FakeWebSocket[] = [];

  readyState = 0;
  onerror: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onopen: (() => void) | null = null;
  sent: string[] = [];
  closed = false;

  constructor(public readonly url: string) {
    FakeWebSocket.instances.push(this);
  }

  send(value: string) {
    this.sent.push(value);
  }

  close() {
    this.readyState = 3;
    this.closed = true;
  }

  open() {
    this.readyState = FakeWebSocket.OPEN;
    this.onopen?.();
  }

  message(payload: unknown) {
    this.onmessage?.({ data: JSON.stringify(payload) } as MessageEvent);
  }

  error() {
    this.onerror?.(new Event("error"));
  }
}

function wsUrl(path: string) {
  return `ws://127.0.0.1:8001${path}`;
}

beforeEach(() => {
  vi.useRealTimers();
  FakeWebSocket.instances = [];
  vi.stubGlobal("WebSocket", FakeWebSocket);
});

describe("sendSpeakingTurn", () => {
  it("streams text WebSocket tokens into one final reply", async () => {
    const streamed: string[] = [];
    const turn = sendSpeakingTurn({
      wsUrl,
      token: "token-1",
      roomId: "coffee-alex",
      mood: "charged",
      message: "Could I get coffee?",
      speechRate: 1,
      transport: "text",
      onToken: (reply) => streamed.push(reply)
    });
    const socket = FakeWebSocket.instances[0];

    expect(socket.url).toContain("/speaking/ws?");
    expect(socket.url).toContain("room_id=coffee-alex");
    expect(socket.url).toContain("mood=charged");

    socket.open();
    expect(socket.sent).toEqual(["Could I get coffee?"]);

    socket.message({ type: "token", value: "Sure, " });
    socket.message({ type: "token", value: "what size?" });
    socket.message({ type: "done" });

    await expect(turn).resolves.toEqual({ finalReply: "Sure, what size?" });
    expect(streamed).toEqual(["Sure, ", "Sure, what size?"]);
    expect(socket.closed).toBe(true);
  });

  it("sends voice turns as JSON and accepts tts text as the final reply", async () => {
    const turn = sendSpeakingTurn({
      wsUrl,
      token: "token-1",
      roomId: "coffee-alex",
      mood: "tired",
      message: "I want coffee",
      speechRate: 0.82,
      transport: "voice",
      onToken: vi.fn()
    });
    const socket = FakeWebSocket.instances[0];

    expect(socket.url).toContain("/speaking/voice-ws?");
    socket.open();
    expect(JSON.parse(socket.sent[0])).toEqual({ type: "user_text", value: "I want coffee", speed: 0.82 });

    socket.message({ type: "assistant_token", value: "Soft mode." });
    socket.message({ type: "tts", text: "Soft mode.", speed: 0.82 });
    socket.message({ type: "done" });

    await expect(turn).resolves.toEqual({ finalReply: "Soft mode." });
  });

  it("sends heartbeat pings while a turn is open", async () => {
    vi.useFakeTimers();
    const turn = sendSpeakingTurn({
      wsUrl,
      token: "token-1",
      roomId: "coffee-alex",
      mood: "charged",
      message: "Still there?",
      speechRate: 1,
      transport: "text",
      heartbeatMs: 25,
      timeoutMs: 500,
      onToken: vi.fn()
    });
    const socket = FakeWebSocket.instances[0];

    socket.open();
    vi.advanceTimersByTime(25);
    expect(socket.sent).toContain(JSON.stringify({ type: "ping" }));

    socket.message({ type: "done" });
    await expect(turn).resolves.toEqual({ finalReply: "" });
  });

  it("rejects if the speaking turn times out", async () => {
    vi.useFakeTimers();
    const turn = sendSpeakingTurn({
      wsUrl,
      token: "token-1",
      roomId: "coffee-alex",
      mood: "steady",
      message: "Timeout test",
      speechRate: 1,
      transport: "text",
      heartbeatMs: 25,
      timeoutMs: 100,
      onToken: vi.fn()
    });
    const socket = FakeWebSocket.instances[0];

    socket.open();
    vi.advanceTimersByTime(101);

    await expect(turn).rejects.toThrow("Speaking stream timed out.");
    expect(socket.closed).toBe(true);
  });
});

describe("requestCallSummary", () => {
  it("requests end_call and resolves the call summary event", async () => {
    const summary = {
      topic: "1 voice turn in coffee alex.",
      new_phrases: ["What would you recommend next?"],
      grammar_feedback: "No repeated grammar pattern yet.",
      turns: 1
    };
    const request = requestCallSummary({ wsUrl, token: "token-1", roomId: "coffee-alex" });
    const socket = FakeWebSocket.instances[0];

    expect(socket.url).toContain("/speaking/voice-ws?");
    socket.open();
    expect(JSON.parse(socket.sent[0])).toEqual({ type: "end_call" });
    socket.message({ type: "call_summary", value: summary });

    await expect(request).resolves.toEqual(summary);
    expect(socket.closed).toBe(true);
  });
});

describe("sendVoiceAudioTurn", () => {
  it("commits audio chunks after session_ready and resolves transcript plus reply", async () => {
    const statuses: unknown[] = [];
    const streamed: string[] = [];
    const turn = sendVoiceAudioTurn({
      wsUrl,
      token: "token-1",
      roomId: "coffee-alex",
      mood: "steady",
      chunks: [{ audioBase64: "ZmFrZS1hdWRpbw==", transcript: "Could I get a latte?" }],
      speechRate: 0.85,
      onStatus: (event) => statuses.push(event),
      onToken: (reply) => streamed.push(reply)
    });
    const socket = FakeWebSocket.instances[0];

    socket.open();
    socket.message({ type: "session_ready", capabilities: { accepts_audio_chunks: true } });
    expect(JSON.parse(socket.sent[0])).toEqual({
      type: "audio_chunk",
      audio_base64: "ZmFrZS1hdWRpbw==",
      transcript: "Could I get a latte?"
    });
    expect(JSON.parse(socket.sent[1])).toEqual({ type: "end_audio", speed: 0.85 });

    socket.message({ type: "stt_status", chunks: 1, bytes: 10, provider: "browser_speech_recognition" });
    socket.message({ type: "transcript", value: "Could I get a latte?", provider: "audio_chunk_metadata" });
    socket.message({ type: "assistant_token", value: "Nice choice. " });
    socket.message({ type: "tts", text: "Nice choice.", speed: 0.85, provider: "client_speech_synthesis" });
    socket.message({ type: "done" });

    await expect(turn).resolves.toEqual({
      finalReply: "Nice choice.",
      transcript: "Could I get a latte?"
    });
    expect(streamed).toEqual(["Nice choice. "]);
    expect(statuses).toHaveLength(4);
  });
});
