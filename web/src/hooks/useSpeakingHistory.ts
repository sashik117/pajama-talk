import { useEffect, type Dispatch } from "react";
import { api, type SpeakingRoomDto } from "../api";
import type { ChatAction, ChatLine } from "../state/chatState";

type SpeakingHistoryOptions = {
  activeRoom: SpeakingRoomDto | null;
  chatDispatch: Dispatch<ChatAction>;
  token: string;
};

export function useSpeakingHistory({ activeRoom, chatDispatch, token }: SpeakingHistoryOptions) {
  useEffect(() => {
    if (!token || !activeRoom) return;
    const roomId = activeRoom.id;
    let cancelled = false;

    api
      .speakingHistory(token, roomId, 40)
      .then((history) => {
        if (cancelled) return;
        const restored: ChatLine[] = history.map((item) => ({ role: item.role, text: item.content }));
        if (restored.length > 0) {
          chatDispatch({ type: "hydrateHistory", roomId, chat: restored });
        }
      })
      .catch(() => undefined);

    return () => {
      cancelled = true;
    };
  }, [token, activeRoom?.id, chatDispatch]);
}
