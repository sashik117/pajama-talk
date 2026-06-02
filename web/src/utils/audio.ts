export type AudioPayload = {
  audioBase64: string;
  mimeType: string;
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
