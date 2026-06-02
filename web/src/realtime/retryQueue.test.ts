import { beforeEach, describe, expect, it, vi } from "vitest";
import { queueRealtimeTurn, queuedRealtimeCount, queuedRealtimeTurns, removeQueuedRealtimeTurn } from "./retryQueue";

function fakeStorage() {
  const data = new Map<string, string>();
  return {
    getItem: (key: string) => data.get(key) ?? null,
    setItem: (key: string, value: string) => data.set(key, value),
    removeItem: (key: string) => data.delete(key)
  };
}

beforeEach(() => {
  vi.stubGlobal("window", { localStorage: fakeStorage() });
});

describe("retryQueue", () => {
  it("persists and removes queued realtime turns", () => {
    const queued = queueRealtimeTurn({
      kind: "text",
      roomId: "coffee-alex",
      mood: "steady",
      message: "Could you repeat that?",
      speechRate: 1,
      transport: "text"
    });

    expect(queuedRealtimeCount("coffee-alex")).toBe(1);
    expect(queuedRealtimeTurns()[0]).toMatchObject({ id: queued.id, message: "Could you repeat that?" });

    removeQueuedRealtimeTurn(queued.id);

    expect(queuedRealtimeCount("coffee-alex")).toBe(0);
  });
});
