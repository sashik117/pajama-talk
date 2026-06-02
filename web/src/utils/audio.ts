export type AudioPayload = {
  audioBase64: string;
  mimeType: string;
};

export type RecordedAudioChunk = {
  audioBase64: string;
  mimeType: string;
  transcript?: string;
};

export async function playAudioPayload(payload: AudioPayload): Promise<void> {
  const bytes = Uint8Array.from(atob(payload.audioBase64), (char) => char.charCodeAt(0));
  const blob = new Blob([bytes], { type: payload.mimeType });
  const url = URL.createObjectURL(blob);
  try {
    const audio = new Audio(url);
    await audio.play();
    await new Promise<void>((resolve) => {
      audio.onended = () => resolve();
      audio.onerror = () => resolve();
    });
  } finally {
    URL.revokeObjectURL(url);
  }
}

export async function blobToBase64(blob: Blob): Promise<string> {
  const bytes = new Uint8Array(await blob.arrayBuffer());
  const chunkSize = 0x8000;
  let binary = "";
  for (let offset = 0; offset < bytes.length; offset += chunkSize) {
    binary += String.fromCharCode(...bytes.subarray(offset, offset + chunkSize));
  }
  return btoa(binary);
}

export function preferredRecordingMimeType(): string {
  if (typeof MediaRecorder === "undefined" || !("isTypeSupported" in MediaRecorder)) return "";
  return (
    [
      "audio/webm;codecs=opus",
      "audio/webm",
      "audio/mp4",
      "audio/ogg;codecs=opus"
    ].find((mimeType) => MediaRecorder.isTypeSupported(mimeType)) ?? ""
  );
}
