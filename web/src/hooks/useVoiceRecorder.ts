import { useRef, useState } from "react";
import { blobToBase64, preferredRecordingMimeType, type RecordedAudioChunk } from "../utils/audio";
import { getSpeechLang } from "../utils/speech";

export type VoiceRecording = {
  chunks: RecordedAudioChunk[];
  transcript: string;
  durationMs: number;
  mimeType: string;
  bytes: number;
};

type VoiceRecorderStatus = "idle" | "recording" | "processing";

type VoiceRecorderOptions = {
  languageCode: string;
  maxMs?: number;
  onTranscript?: (text: string) => void;
};

export function useVoiceRecorder({ languageCode, maxMs = 12000, onTranscript }: VoiceRecorderOptions) {
  const [isRecording, setIsRecording] = useState(false);
  const [status, setStatus] = useState<VoiceRecorderStatus>("idle");
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState("");

  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const startedAtRef = useRef(0);
  const mimeTypeRef = useRef("audio/webm");
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const transcriptRef = useRef("");
  const stopResolverRef = useRef<((recording: VoiceRecording | null) => void) | null>(null);

  const isSupported = typeof navigator !== "undefined" && Boolean(navigator.mediaDevices?.getUserMedia) && typeof MediaRecorder !== "undefined";

  function clearRecordingTimeout() {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }

  function stopSpeechHint() {
    recognitionRef.current?.stop?.();
    recognitionRef.current?.abort?.();
    recognitionRef.current = null;
  }

  function releaseStream() {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    recorderRef.current = null;
  }

  function startSpeechHint() {
    const SpeechCtor = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechCtor) return;
    const recognition = new SpeechCtor();
    recognition.lang = getSpeechLang(languageCode);
    recognition.interimResults = true;
    recognition.continuous = true;
    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const nextTranscript = Array.from(event.results)
        .map((result) => result[0]?.transcript ?? "")
        .join(" ")
        .trim();
      transcriptRef.current = nextTranscript;
      setTranscript(nextTranscript);
      onTranscript?.(nextTranscript);
    };
    recognition.onerror = null;
    recognition.onend = () => {
      recognitionRef.current = null;
    };
    try {
      recognition.start();
      recognitionRef.current = recognition;
    } catch {
      recognitionRef.current = null;
    }
  }

  async function finalizeRecording(recorder: MediaRecorder) {
    clearRecordingTimeout();
    stopSpeechHint();
    const blobs = chunksRef.current;
    const durationMs = startedAtRef.current ? Date.now() - startedAtRef.current : 0;
    const mimeType = recorder.mimeType || mimeTypeRef.current;
    const transcriptValue = transcriptRef.current.trim();
    const resolver = stopResolverRef.current;
    stopResolverRef.current = null;
    releaseStream();
    setIsRecording(false);
    setStatus("idle");

    if (blobs.length === 0) {
      resolver?.(null);
      return;
    }

    try {
      const chunks = await Promise.all(
        blobs.map(async (blob) => ({
          audioBase64: await blobToBase64(blob),
          mimeType: blob.type || mimeType,
          transcript: transcriptValue || undefined
        }))
      );
      resolver?.({
        chunks,
        transcript: transcriptValue,
        durationMs,
        mimeType,
        bytes: blobs.reduce((total, blob) => total + blob.size, 0)
      });
    } catch {
      setError("recording-encode-failed");
      resolver?.(null);
    }
  }

  async function startRecording() {
    if (recorderRef.current?.state === "recording") return;
    if (!isSupported) {
      setError("media-recorder-unavailable");
      return;
    }

    try {
      setError("");
      setTranscript("");
      transcriptRef.current = "";
      chunksRef.current = [];
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
      });
      streamRef.current = stream;
      const mimeType = preferredRecordingMimeType();
      mimeTypeRef.current = mimeType || "audio/webm";
      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
      recorderRef.current = recorder;
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      recorder.onerror = () => {
        setError("recording-failed");
        void stopRecording();
      };
      recorder.onstop = () => {
        void finalizeRecording(recorder);
      };
      startedAtRef.current = Date.now();
      setStatus("recording");
      setIsRecording(true);
      recorder.start(900);
      startSpeechHint();
      timeoutRef.current = setTimeout(() => {
        void stopRecording();
      }, maxMs);
    } catch {
      clearRecordingTimeout();
      releaseStream();
      stopSpeechHint();
      setIsRecording(false);
      setStatus("idle");
      setError("microphone-denied");
    }
  }

  function stopRecording(): Promise<VoiceRecording | null> {
    clearRecordingTimeout();
    stopSpeechHint();
    const recorder = recorderRef.current;
    if (!recorder || recorder.state === "inactive") {
      releaseStream();
      setIsRecording(false);
      setStatus("idle");
      return Promise.resolve(null);
    }
    setStatus("processing");
    return new Promise((resolve) => {
      stopResolverRef.current = resolve;
      recorder.stop();
    });
  }

  function resetRecorder() {
    clearRecordingTimeout();
    stopSpeechHint();
    releaseStream();
    chunksRef.current = [];
    stopResolverRef.current?.(null);
    stopResolverRef.current = null;
    setIsRecording(false);
    setStatus("idle");
    setTranscript("");
    setError("");
  }

  return {
    error,
    isRecording,
    isSupported,
    resetRecorder,
    startRecording,
    status,
    stopRecording,
    transcript
  };
}
