import { useEffect, useState, type Dispatch } from "react";
import { api, type CallSummaryDto, type SpeakingRoomDto } from "../api";
import {
  requestCallSummary,
  sendSpeakingTurn,
  sendVoiceAudioTurn,
  type SpeakingTransport,
  type VoiceAudioChunk
} from "../realtime/speakingClient";
import {
  queueRealtimeTurn,
  queuedRealtimeCount,
  queuedRealtimeTurns,
  removeQueuedRealtimeTurn,
  type QueuedRealtimeTurn
} from "../realtime/retryQueue";
import type { ChatAction, ChatLine, MoodKey } from "../state/chatState";
import { playAudioPayload, type AudioPayload } from "../utils/audio";
import { speakText } from "../utils/speech";

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
  const [queuedTurnsCount, setQueuedTurnsCount] = useState(() => queuedRealtimeCount(activeRoom?.id));

  useEffect(() => {
    setQueuedTurnsCount(queuedRealtimeCount(activeRoom?.id));
  }, [activeRoom?.id]);

  async function playReply(finalReply: string, audio: AudioPayload | undefined, speechRate: number) {
    if (!finalReply) return;
    if (audio) {
      try {
        await playAudioPayload(audio);
        return;
      } catch {
        speakText(finalReply, learningCode, speechRate);
        return;
      }
    }
    speakText(finalReply, learningCode, speechRate);
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

  async function sendMessage(
    message: string,
    speechRate = 1,
    transport: SpeakingTransport = "text",
    queueOnFailure = true,
    moodOverride: MoodKey = activeMood
  ): Promise<boolean> {
    if (!token || !activeRoom || !message.trim() || isStreaming) return false;
    const normalizedMessage = message.trim();
    chatDispatch({ type: "appendUserTurn", message: normalizedMessage });
    let finalReply = "";
    setIsStreaming(true);
    try {
      const result = await sendSpeakingTurn({
        wsUrl: api.wsUrl,
        token,
        roomId: activeRoom.id,
        mood: moodOverride,
        message: normalizedMessage,
        speechRate,
        transport,
        retries: 1,
        onToken: (reply) => chatDispatch({ type: "replaceAssistantDraft", text: reply })
      });
      finalReply = result.finalReply;
      await playReply(finalReply, result.audio, speechRate);
    } catch (err) {
      if (queueOnFailure) {
        queueRealtimeTurn({ kind: "text", roomId: activeRoom.id, mood: moodOverride, message: normalizedMessage, speechRate, transport });
        setQueuedTurnsCount(queuedRealtimeCount(activeRoom.id));
        chatDispatch({ type: "replaceAssistantDraft", text: "Saved locally. Retry when the connection is back." });
      }
      setError(err instanceof Error ? err.message : "Speaking stream failed.");
      return false;
    } finally {
      setIsStreaming(false);
    }

    await refreshGrammar();
    return true;
  }

  async function sendAudioMessage(
    chunks: VoiceAudioChunk[],
    transcriptHint = "",
    speechRate = 1,
    queueOnFailure = true,
    moodOverride: MoodKey = activeMood
  ): Promise<boolean> {
    if (!token || !activeRoom || chunks.length === 0 || isStreaming) return false;
    const displayText = transcriptHint.trim() || "Voice note";
    chatDispatch({ type: "appendUserTurn", message: displayText });
    setIsStreaming(true);
    try {
      const result = await sendVoiceAudioTurn({
        wsUrl: api.wsUrl,
        token,
        roomId: activeRoom.id,
        mood: moodOverride,
        chunks,
        transcriptHint,
        speechRate,
        retries: 1,
        onToken: (reply) => chatDispatch({ type: "replaceAssistantDraft", text: reply })
      });
      const transcript = result.transcript.trim();
      if (transcript && transcript !== displayText) {
        chatDispatch({ type: "replaceLastUserTurn", message: transcript });
      }
      await playReply(result.finalReply, result.audio, speechRate);
    } catch (err) {
      if (queueOnFailure) {
        queueRealtimeTurn({ kind: "audio", roomId: activeRoom.id, mood: moodOverride, chunks, transcriptHint, speechRate });
        setQueuedTurnsCount(queuedRealtimeCount(activeRoom.id));
        chatDispatch({ type: "replaceAssistantDraft", text: "Saved locally. Retry when the connection is back." });
      }
      setError(err instanceof Error ? err.message : "Voice audio stream failed.");
      return false;
    } finally {
      setIsStreaming(false);
    }

    await refreshGrammar();
    return true;
  }

  async function replayQueuedTurns() {
    if (!token || !activeRoom || isStreaming) return;
    const turns = queuedRealtimeTurns().filter((turn) => turn.roomId === activeRoom.id);
    for (const turn of turns) {
      const ok = await replayQueuedTurn(turn);
      if (!ok) break;
      removeQueuedRealtimeTurn(turn.id);
    }
    setQueuedTurnsCount(queuedRealtimeCount(activeRoom.id));
  }

  async function replayQueuedTurn(turn: QueuedRealtimeTurn): Promise<boolean> {
    if (turn.kind === "text") {
      return sendMessage(turn.message, turn.speechRate, turn.transport, false, turn.mood);
    }
    return sendAudioMessage(turn.chunks, turn.transcriptHint, turn.speechRate, false, turn.mood);
  }

  async function loadCallSummary(roomId: string): Promise<CallSummaryDto> {
    if (!token) throw new Error("No active session.");
    return requestCallSummary({ wsUrl: api.wsUrl, token, roomId });
  }

  return { isStreaming, loadCallSummary, loadHints, queuedTurnsCount, replayQueuedTurns, sendAudioMessage, sendMessage };
}
