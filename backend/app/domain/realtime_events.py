from typing import Any, Literal, TypedDict


ServerEventType = Literal[
    "session_ready",
    "stt_status",
    "transcript",
    "token",
    "assistant_token",
    "tts",
    "call_summary",
    "pong",
    "error",
    "done",
]

TokenEventType = Literal["token", "assistant_token"]


class RealtimeEvent(TypedDict, total=False):
    type: ServerEventType
    value: Any
    text: str
    format: str
    speed: float | int
    stt: str
    tts: str
    provider: str
    confidence: float
    chunks: int
    bytes: int
    capabilities: dict[str, object]
    audio_base64: str | None
    mime_type: str | None


def session_ready_event(capabilities: dict[str, object] | None = None) -> RealtimeEvent:
    return {
        "type": "session_ready",
        "stt": "browser-stt-now; whisper-audio-chunks-ready",
        "tts": "client-speech-synthesis-now; provider-audio-chunks-ready",
        "capabilities": capabilities or {},
    }


def token_event(event_type: TokenEventType, value: str) -> RealtimeEvent:
    return {"type": event_type, "value": value}


def status_event(value: str, details: dict[str, object] | None = None) -> RealtimeEvent:
    return {"type": "stt_status", "value": value, **(details or {})}


def transcript_event(value: str, provider: str = "browser_speech_recognition", confidence: float = 1.0) -> RealtimeEvent:
    return {"type": "transcript", "value": value, "provider": provider, "confidence": confidence}


def tts_event(
    text: str,
    speed: float | int,
    provider: str = "client_speech_synthesis",
    audio_base64: str | None = None,
    mime_type: str | None = None,
    audio_format: str = "client_speech_synthesis",
) -> RealtimeEvent:
    return {
        "type": "tts",
        "format": audio_format,
        "text": text,
        "speed": speed,
        "provider": provider,
        "audio_base64": audio_base64,
        "mime_type": mime_type,
    }


def call_summary_event(value: dict[str, object]) -> RealtimeEvent:
    return {"type": "call_summary", "value": value}


def pong_event() -> RealtimeEvent:
    return {"type": "pong"}


def error_event(value: str) -> RealtimeEvent:
    return {"type": "error", "value": value}


def done_event() -> RealtimeEvent:
    return {"type": "done"}
