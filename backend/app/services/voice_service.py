from __future__ import annotations

import base64
from typing import Any, Protocol

import httpx

from app.core.config import settings
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


class OpenAISpeechToTextProvider:
    name = "openai_audio_transcriptions"

    def __init__(self, api_key: str, model: str, timeout_seconds: int) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.fallback = BrowserSpeechFallbackProvider()

    def transcribe(self, buffer: VoiceSessionBuffer, fallback_text: str = "") -> SpeechTranscript:
        if not buffer.audio_bytes:
            return self.fallback.transcribe(buffer, fallback_text=fallback_text)

        extension = _extension_for_mime(buffer.mime_type)
        try:
            response = httpx.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                data={"model": self.model, "response_format": "json"},
                files={"file": (f"pajamatalk-turn.{extension}", buffer.audio_bytes, buffer.mime_type)},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            text = str(response.json().get("text", "")).strip()
            if text:
                return SpeechTranscript(text=text, provider=self.name, confidence=1.0)
        except (httpx.HTTPError, ValueError, TypeError):
            pass

        return self.fallback.transcribe(buffer, fallback_text=fallback_text)


class OpenAITextToSpeechProvider:
    name = "openai_audio_speech"

    def __init__(self, api_key: str, model: str, voice: str, response_format: str, timeout_seconds: int) -> None:
        self.api_key = api_key
        self.model = model
        self.voice = voice
        self.response_format = response_format
        self.timeout_seconds = timeout_seconds
        self.fallback = ClientSpeechSynthesisProvider()

    def synthesize(self, text: str, speed: float, language_code: str) -> SynthesizedSpeech:
        clean_speed = max(0.6, min(speed, 1.35))
        try:
            response = httpx.post(
                "https://api.openai.com/v1/audio/speech",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "voice": self.voice,
                    "input": text,
                    "response_format": self.response_format,
                    "speed": clean_speed,
                    "instructions": _tts_instructions(language_code),
                },
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            audio_bytes = response.content
            if audio_bytes:
                return SynthesizedSpeech(
                    text=text,
                    provider=self.name,
                    format="audio_base64",
                    speed=clean_speed,
                    audio_base64=base64.b64encode(audio_bytes).decode("ascii"),
                    mime_type=_mime_for_audio_format(self.response_format),
                )
        except httpx.HTTPError:
            pass

        return self.fallback.synthesize(text, clean_speed, language_code)


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
        default_stt, default_tts = _default_voice_providers()
        self.stt_provider = stt_provider or default_stt
        self.tts_provider = tts_provider or default_tts

    def capabilities(self) -> dict[str, object]:
        return {
            "stt_provider": self.stt_provider.name,
            "tts_provider": self.tts_provider.name,
            "accepts_audio_chunks": True,
            "accepts_browser_transcript": True,
            "streams_reply_tokens": True,
            "audio_output": "audio_base64" if self.tts_provider.name.startswith("openai") else "client_speech_synthesis",
        }

    def accept_audio_chunk(self, payload: dict[str, Any]) -> dict[str, object]:
        raw_audio = payload.get("audio_base64") or payload.get("value") or payload.get("audio")
        if isinstance(raw_audio, str) and raw_audio:
            chunk = _decode_audio_chunk(raw_audio)
            self.buffer.audio_chunks.append(chunk)
            self.buffer.bytes_received += len(chunk)
        elif isinstance(raw_audio, bytes):
            self.buffer.audio_chunks.append(raw_audio)
            self.buffer.bytes_received += len(raw_audio)
        mime_type = str(payload.get("mime_type") or payload.get("mimeType") or "").strip()
        if mime_type:
            self.buffer.mime_type = mime_type

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


def _decode_audio_chunk(value: str) -> bytes:
    try:
        return base64.b64decode(value, validate=True)
    except Exception:
        return value.encode("utf-8")


def _default_voice_providers() -> tuple[SpeechToTextProvider, TextToSpeechProvider]:
    if settings.openai_api_key:
        return (
            OpenAISpeechToTextProvider(
                api_key=settings.openai_api_key,
                model=settings.openai_stt_model,
                timeout_seconds=settings.voice_provider_timeout_seconds,
            ),
            OpenAITextToSpeechProvider(
                api_key=settings.openai_api_key,
                model=settings.openai_tts_model,
                voice=settings.openai_tts_voice,
                response_format=settings.openai_tts_format,
                timeout_seconds=settings.voice_provider_timeout_seconds,
            ),
        )
    return BrowserSpeechFallbackProvider(), ClientSpeechSynthesisProvider()


def _extension_for_mime(mime_type: str) -> str:
    normalized = mime_type.lower()
    if "mpeg" in normalized or "mp3" in normalized:
        return "mp3"
    if "mp4" in normalized:
        return "mp4"
    if "m4a" in normalized:
        return "m4a"
    if "wav" in normalized:
        return "wav"
    if "webm" in normalized:
        return "webm"
    return "webm"


def _mime_for_audio_format(response_format: str) -> str:
    return {
        "mp3": "audio/mpeg",
        "opus": "audio/opus",
        "aac": "audio/aac",
        "flac": "audio/flac",
        "wav": "audio/wav",
        "pcm": "audio/pcm",
    }.get(response_format.lower(), "audio/mpeg")


def _tts_instructions(language_code: str) -> str:
    return (
        "Speak naturally as a kind language tutor. Keep the pace clear and beginner-friendly. "
        f"The learner is practicing language code {language_code}."
    )
