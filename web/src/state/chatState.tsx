import { createContext, useContext, useEffect, useReducer } from "react";
import type { Dispatch, ReactNode } from "react";
import type { SpeakingHintsDto, SpeakingRoomDto } from "../api";

export type ChatLine = { role: "user" | "assistant"; text: string };
export type MoodKey = "tired" | "charged" | "hard" | "steady";

export type ChatState = {
  activeRoom: SpeakingRoomDto | null;
  activeMood: MoodKey;
  chat: ChatLine[];
  hints: SpeakingHintsDto | null;
};

export type ChatAction =
  | { type: "enterRoom"; room: SpeakingRoomDto; mood: MoodKey; intro: string }
  | { type: "leaveRoom" }
  | { type: "setHints"; hints: SpeakingHintsDto | null }
  | { type: "appendUserTurn"; message: string }
  | { type: "replaceLastUserTurn"; message: string }
  | { type: "replaceAssistantDraft"; text: string }
  | { type: "resetSession" };

const CHAT_STORAGE_KEY = "pajamatalk.speakingSession.v1";

const initialChatState: ChatState = {
  activeRoom: null,
  activeMood: "steady",
  chat: [],
  hints: null
};

export function createInitialChatState(): ChatState {
  const stored = readStoredChatState();
  return stored ?? initialChatState;
}

export function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case "enterRoom":
      return {
        activeRoom: action.room,
        activeMood: action.mood,
        chat: [{ role: "assistant", text: action.intro }],
        hints: null
      };
    case "leaveRoom":
    case "resetSession":
      return initialChatState;
    case "setHints":
      return { ...state, hints: action.hints };
    case "appendUserTurn":
      return {
        ...state,
        hints: null,
        chat: [...state.chat, { role: "user", text: action.message }, { role: "assistant", text: "" }]
      };
    case "replaceLastUserTurn": {
      const userIndex = [...state.chat].reverse().findIndex((line) => line.role === "user");
      if (userIndex < 0) return state;
      const index = state.chat.length - 1 - userIndex;
      return {
        ...state,
        chat: state.chat.map((line, lineIndex) => (lineIndex === index ? { ...line, text: action.message } : line))
      };
    }
    case "replaceAssistantDraft":
      if (state.chat.length === 0) return state;
      return {
        ...state,
        chat: [...state.chat.slice(0, -1), { role: "assistant", text: action.text }]
      };
    default:
      return state;
  }
}

const ChatStateContext = createContext<ChatState | null>(null);
const ChatDispatchContext = createContext<Dispatch<ChatAction> | null>(null);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(chatReducer, undefined, createInitialChatState);

  useEffect(() => {
    persistChatState(state);
  }, [state]);

  return (
    <ChatStateContext.Provider value={state}>
      <ChatDispatchContext.Provider value={dispatch}>{children}</ChatDispatchContext.Provider>
    </ChatStateContext.Provider>
  );
}

export function useChatState() {
  const state = useContext(ChatStateContext);
  if (!state) throw new Error("useChatState must be used inside ChatProvider.");
  return state;
}

export function useChatDispatch() {
  const dispatch = useContext(ChatDispatchContext);
  if (!dispatch) throw new Error("useChatDispatch must be used inside ChatProvider.");
  return dispatch;
}

function storage(): Storage | null {
  try {
    return typeof window === "undefined" ? null : window.localStorage;
  } catch {
    return null;
  }
}

function readStoredChatState(): ChatState | null {
  const store = storage();
  if (!store) return null;
  try {
    const parsed = JSON.parse(store.getItem(CHAT_STORAGE_KEY) ?? "null") as Partial<ChatState> | null;
    if (!parsed?.activeRoom || !isMoodKey(parsed.activeMood) || !Array.isArray(parsed.chat)) return null;
    const chat = parsed.chat.filter(isChatLine).slice(-80);
    if (chat.length === 0) return null;
    return { activeRoom: parsed.activeRoom as SpeakingRoomDto, activeMood: parsed.activeMood, chat, hints: null };
  } catch {
    return null;
  }
}

function persistChatState(state: ChatState) {
  const store = storage();
  if (!store) return;
  if (!state.activeRoom || state.chat.length === 0) {
    store.removeItem(CHAT_STORAGE_KEY);
    return;
  }
  store.setItem(CHAT_STORAGE_KEY, JSON.stringify({ ...state, hints: null, chat: state.chat.slice(-80) }));
}

function isMoodKey(value: unknown): value is MoodKey {
  return value === "tired" || value === "charged" || value === "hard" || value === "steady";
}

function isChatLine(value: unknown): value is ChatLine {
  if (!value || typeof value !== "object") return false;
  const line = value as Partial<ChatLine>;
  return (line.role === "user" || line.role === "assistant") && typeof line.text === "string";
}
