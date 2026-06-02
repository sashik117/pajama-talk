import { useState, type Dispatch } from "react";
import { api, type CallSummaryDto, type SpeakingRoomDto } from "../api";
import { requestCallSummary, sendSpeakingTurn, type SpeakingTransport } from "../realtime/speakingClient";
import type { ChatAction, ChatLine, MoodKey } from "../state/chatState";
import { playAudioPayload, type AudioPayload } from "../utils/audio";
import { getSpeechLang } from "../utils/speech";

type SpeakingControllerOptions = {
  activeMood: MoodKey;
  activeRoom: SpeakingRoomDto | null;
  chat: ChatLine[];
  chatDispatch: Dispatch<ChatAction>;
  learningCode: string;
  refreshGrammar: () => Promise<void>;
  setError: (message: string) => void;
  token: string;
};

export function useSpeakingController({
  activeMood,
  activeRoom,
  chat,
  chatDispatch,
  learningCode,
  refreshGrammar,
  setError,
  token
}: SpeakingControllerOptions) {
  const [isStreaming, setIsStreaming] = useState(false);

  function speakWithBrowser(text: string, speechRate: number) {
    if (!text || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = getSpeechLang(learningCode);
    utterance.rate = speechRate;
    window.speechSynthesis.speak(utterance);
  }

  async function playReply(finalReply: string, audio: AudioPayload | undefined, speechRate: number) {
    if (!finalReply) return;
    if (audio) {
      try {
        await playAudioPayload(audio);
        return;
      } catch {
        speakWithBrowser(finalReply, speechRate);
        return;
      }
    }
    speakWithBrowser(finalReply, speechRate);
  }

  async function loadHints() {
    if (!token || !activeRoom) return;
    const last = [...chat].reverse().find((line) => line.role === "assistant")?.text ?? activeRoom.prompt;
    try {
      chatDispatch({ type: "setHints", hints: await api.speakingHints(token, activeRoom.id, last, learningCode) });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Hints failed.");
    }
  }

  async function sendMessage(message: string, speechRate = 1, transport: SpeakingTransport = "text") {
    if (!token || !activeRoom || !message.trim() || isStreaming) return;
    const normalizedMessage = message.trim();
    chatDispatch({ type: "appendUserTurn", message: normalizedMessage });
    let finalReply = "";
    setIsStreaming(true);
    try {
      const result = await sendSpeakingTurn({
        wsUrl: api.wsUrl,
        token,
        roomId: activeRoom.id,
        mood: activeMood,
        message: normalizedMessage,
        speechRate,
        transport,
        retries: 1,
        onToken: (reply) => chatDispatch({ type: "replaceAssistantDraft", text: reply })
      });
      finalReply = result.finalReply;
      await playReply(finalReply, result.audio, speechRate);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Speaking stream failed.");
    } finally {
      setIsStreaming(false);
    }

    await refreshGrammar();
  }

  async function loadCallSummary(roomId: string): Promise<CallSummaryDto> {
    if (!token) throw new Error("No active session.");
    return requestCallSummary({ wsUrl: api.wsUrl, token, roomId });
  }

  return { isStreaming, loadCallSummary, loadHints, sendMessage };
}
