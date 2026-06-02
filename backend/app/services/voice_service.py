from __future__ import annotations

import base64
from typing import Any, Protocol

from app.domain.voice import SpeechTranscript, SynthesizedSpeech, VoiceSessionBuffer


class SpeechToTextProvider(Protocol):
    name: str

    def transcribe(self, buffer: VoiceSessionBuffer, fallback_text: str = "") -> SpeechTranscript:
        ...


class TextToSpeechProvider(Protocol):
    name: str

    def synthesize(self, text: str, speed: float, language_code: str) -> SynthesizedSpeech:
        ...


class BrowserSpeechFallbackProvider:
    name = "browser_speech_recognition"

    def transcribe(self, buffer: VoiceSessionBuffer, fallback_text: str = "") -> SpeechTranscript:
        hinted_text = " ".join(item for item in buffer.transcript_hints if item).strip()
        text = fallback_text.strip() or hinted_text
        provider = self.name if fallback_text.strip() else "audio_chunk_metadata"
        return SpeechTranscript(text=text, provider=provider, confidence=1.0 if text else 0.0)


class ClientSpeechSynthesisProvider:
    name = "client_speech_synthesis"

    def synthesize(self, text: str, speed: float, language_code: str) -> SynthesizedSpeech:
        return SynthesizedSpeech(
            text=text,
            provider=self.name,
            format="client_speech_synthesis",
            speed=max(0.6, min(speed, 1.35)),
        )


class VoiceRealtimeService:
    """Owns voice session state and provider fallback decisions."""

    def __init__(
        self,
        language_code: str,
        stt_provider: SpeechToTextProvider | None = None,
        tts_provider: TextToSpeechProvider | None = None,
    ) -> None:
        self.language_code = language_code
        self.buffer = VoiceSessionBuffer()
        self.stt_provider = stt_provider or BrowserSpeechFallbackProvider()
        self.tts_provider = tts_provider or ClientSpeechSynthesisProvider()

    def capabilities(self) -> dict[str, object]:
        return {
            "stt_provider": self.stt_provider.name,
            "tts_provider": self.tts_provider.name,
            "accepts_audio_chunks": True,
            "accepts_browser_transcript": True,
            "streams_reply_tokens": True,
            "audio_output": "client_speech_synthesis",
        }

    def accept_audio_chunk(self, payload: dict[str, Any]) -> dict[str, object]:
        raw_audio = payload.get("audio_base64") or payload.get("value") or payload.get("audio")
        if isinstance(raw_audio, str) and raw_audio:
            self.buffer.bytes_received += _decoded_size(raw_audio)
        elif isinstance(raw_audio, bytes):
            self.buffer.bytes_received += len(raw_audio)

        hint = str(payload.get("transcript") or payload.get("text") or "").strip()
        if hint:
            self.buffer.transcript_hints.append(hint)

        self.buffer.chunks += 1
        return {
            "chunks": self.buffer.chunks,
            "bytes": self.buffer.bytes_received,
            "provider": self.stt_provider.name,
        }

    def transcribe_turn(self, payload: dict[str, Any] | None = None) -> SpeechTranscript:
        payload = payload or {}
        fallback_text = str(payload.get("transcript") or payload.get("text") or payload.get("value") or "").strip()
        transcript = self.stt_provider.transcribe(self.buffer, fallback_text=fallback_text)
        self.buffer.clear()
        return transcript

    def synthesize_reply(self, text: str, speed: float) -> SynthesizedSpeech:
        return self.tts_provider.synthesize(text=text, speed=speed, language_code=self.language_code)


def _decoded_size(value: str) -> int:
    try:
        return len(base64.b64decode(value, validate=True))
    except Exception:
        return len(value.encode("utf-8"))
