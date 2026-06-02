import { beforeEach, describe, expect, it, vi } from "vitest";
import { chatReducer, createInitialChatState, type ChatState } from "./chatState";

const room = {
  id: "coffee-alex",
  title: "Lo-fi Coffee",
  character: "Alex",
  vibe: "soft",
  prompt: "Order coffee.",
  accent_color: "#F3B6A8"
};

function fakeStorage(seed: Record<string, string> = {}) {
  const data = new Map(Object.entries(seed));
  return {
    getItem: (key: string) => data.get(key) ?? null,
    setItem: (key: string, value: string) => data.set(key, value),
    removeItem: (key: string) => data.delete(key)
  };
}

beforeEach(() => {
  vi.unstubAllGlobals();
});

describe("chatState", () => {
  it("starts a room with one assistant intro", () => {
    const state = chatReducer(createInitialChatState(), {
      type: "enterRoom",
      room,
      mood: "tired",
      intro: "Soft mode today."
    });

    expect(state.activeRoom?.id).toBe("coffee-alex");
    expect(state.activeMood).toBe("tired");
    expect(state.chat).toEqual([{ role: "assistant", text: "Soft mode today." }]);
  });

  it("replaces the latest user bubble after STT returns a transcript", () => {
    const base: ChatState = {
      activeRoom: room,
      activeMood: "steady",
      hints: null,
      chat: [{ role: "user", text: "Voice note" }, { role: "assistant", text: "" }]
    };

    const state = chatReducer(base, { type: "replaceLastUserTurn", message: "Could I get a latte?" });

    expect(state.chat[0].text).toBe("Could I get a latte?");
    expect(state.chat[1].role).toBe("assistant");
  });

  it("hydrates a stored speaking session", () => {
    vi.stubGlobal("window", {
      localStorage: fakeStorage({
        "pajamatalk.speakingSession.v1": JSON.stringify({
          activeRoom: room,
          activeMood: "charged",
          hints: { simple: "x", conversational: "y", spicy: "z" },
          chat: [{ role: "assistant", text: "Welcome back." }]
        })
      })
    });

    const state = createInitialChatState();

    expect(state.activeRoom?.id).toBe("coffee-alex");
    expect(state.activeMood).toBe("charged");
    expect(state.hints).toBeNull();
    expect(state.chat[0].text).toBe("Welcome back.");
  });

  it("hydrates server history only for the active room", () => {
    const base = chatReducer(createInitialChatState(), {
      type: "enterRoom",
      room,
      mood: "steady",
      intro: "Intro."
    });

    const updated = chatReducer(base, {
      type: "hydrateHistory",
      roomId: "coffee-alex",
      chat: [
        { role: "user", text: "Could I get a latte?" },
        { role: "assistant", text: "Nice choice." }
      ]
    });
    const ignored = chatReducer(updated, {
      type: "hydrateHistory",
      roomId: "airport-mia",
      chat: [{ role: "assistant", text: "Wrong room." }]
    });

    expect(updated.chat[0].text).toBe("Could I get a latte?");
    expect(ignored.chat).toEqual(updated.chat);
  });

  it("keeps a longer local speaking session instead of overwriting it with stale history", () => {
    const base: ChatState = {
      activeRoom: room,
      activeMood: "steady",
      hints: null,
      chat: [
        { role: "assistant", text: "Welcome." },
        { role: "user", text: "Local turn." },
        { role: "assistant", text: "Local reply." }
      ]
    };

    const state = chatReducer(base, {
      type: "hydrateHistory",
      roomId: "coffee-alex",
      chat: [
        { role: "user", text: "Older server turn." },
        { role: "assistant", text: "Older server reply." }
      ]
    });

    expect(state.chat).toEqual(base.chat);
  });
});
