import { createContext, useContext, useReducer } from "react";
import type { Dispatch, ReactNode } from "react";
import type { SpeakingHintsDto, SpeakingRoomDto } from "../api";

export type ChatLine = { role: "user" | "assistant"; text: string };
export type MoodKey = "tired" | "charged" | "hard" | "steady";

type ChatState = {
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
  | { type: "replaceAssistantDraft"; text: string }
  | { type: "resetSession" };

const initialChatState: ChatState = {
  activeRoom: null,
  activeMood: "steady",
  chat: [],
  hints: null
};

function chatReducer(state: ChatState, action: ChatAction): ChatState {
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
  const [state, dispatch] = useReducer(chatReducer, initialChatState);

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
