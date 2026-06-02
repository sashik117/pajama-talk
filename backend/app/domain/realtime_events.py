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


def session_ready_event() -> RealtimeEvent:
    return {
        "type": "session_ready",
        "stt": "browser-stt-now; whisper-audio-chunks-ready",
        "tts": "client-speech-synthesis-now; provider-audio-chunks-ready",
    }


def token_event(event_type: TokenEventType, value: str) -> RealtimeEvent:
    return {"type": event_type, "value": value}


def status_event(value: str) -> RealtimeEvent:
    return {"type": "stt_status", "value": value}


def transcript_event(value: str) -> RealtimeEvent:
    return {"type": "transcript", "value": value}


def tts_event(text: str, speed: float | int) -> RealtimeEvent:
    return {"type": "tts", "format": "client_speech_synthesis", "text": text, "speed": speed}


def call_summary_event(value: dict[str, object]) -> RealtimeEvent:
    return {"type": "call_summary", "value": value}


def pong_event() -> RealtimeEvent:
    return {"type": "pong"}


def error_event(value: str) -> RealtimeEvent:
    return {"type": "error", "value": value}


def done_event() -> RealtimeEvent:
    return {"type": "done"}
