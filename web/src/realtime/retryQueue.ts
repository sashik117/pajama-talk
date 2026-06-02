import type { SpeakingTransport, VoiceAudioChunk } from "./speakingClient";
import type { MoodKey } from "../state/chatState";

const STORAGE_KEY = "pajamatalk.realtimeQueue.v1";

type QueuedTextTurn = {
  id: string;
  kind: "text";
  createdAt: number;
  roomId: string;
  mood: MoodKey;
  message: string;
  speechRate: number;
  transport: SpeakingTransport;
};

type QueuedAudioTurn = {
  id: string;
  kind: "audio";
  createdAt: number;
  roomId: string;
  mood: MoodKey;
  chunks: VoiceAudioChunk[];
  transcriptHint?: string;
  speechRate: number;
};

export type QueuedRealtimeTurn = QueuedTextTurn | QueuedAudioTurn;
export type NewQueuedRealtimeTurn = Omit<QueuedTextTurn, "id" | "createdAt"> | Omit<QueuedAudioTurn, "id" | "createdAt">;

function storage(): Storage | null {
  try {
    return typeof window === "undefined" ? null : window.localStorage;
  } catch {
    return null;
  }
}

function readQueue(): QueuedRealtimeTurn[] {
  const store = storage();
  if (!store) return [];
  try {
    const parsed = JSON.parse(store.getItem(STORAGE_KEY) ?? "[]");
    return Array.isArray(parsed) ? parsed.filter(isQueuedTurn) : [];
  } catch {
    return [];
  }
}

function writeQueue(queue: QueuedRealtimeTurn[]) {
  const store = storage();
  if (!store) return;
  store.setItem(STORAGE_KEY, JSON.stringify(queue.slice(-12)));
}

function isQueuedTurn(value: unknown): value is QueuedRealtimeTurn {
  if (!value || typeof value !== "object") return false;
  const item = value as Partial<QueuedRealtimeTurn>;
  if (!item.id || !item.roomId || !item.kind || !item.createdAt) return false;
  if (item.kind === "text") return typeof item.message === "string";
  if (item.kind === "audio") return Array.isArray(item.chunks);
  return false;
}

export function queuedRealtimeTurns(): QueuedRealtimeTurn[] {
  return readQueue();
}

export function queueRealtimeTurn(turn: NewQueuedRealtimeTurn): QueuedRealtimeTurn {
  const queued = { ...turn, id: `${Date.now()}-${Math.random().toString(36).slice(2)}`, createdAt: Date.now() } as QueuedRealtimeTurn;
  writeQueue([...readQueue(), queued]);
  return queued;
}

export function removeQueuedRealtimeTurn(id: string) {
  writeQueue(readQueue().filter((turn) => turn.id !== id));
}

export function queuedRealtimeCount(roomId?: string): number {
  const queue = readQueue();
  return roomId ? queue.filter((turn) => turn.roomId === roomId).length : queue.length;
}
