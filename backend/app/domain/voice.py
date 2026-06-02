from dataclasses import dataclass, field


@dataclass
class SpeechTranscript:
    text: str
    provider: str
    confidence: float = 1.0


@dataclass
class SynthesizedSpeech:
    text: str
    provider: str
    format: str
    speed: float
    audio_base64: str | None = None
    mime_type: str | None = None


@dataclass
class VoiceSessionBuffer:
    chunks: int = 0
    bytes_received: int = 0
    transcript_hints: list[str] = field(default_factory=list)
    audio_chunks: list[bytes] = field(default_factory=list)
    mime_type: str = "audio/webm"

    @property
    def audio_bytes(self) -> bytes:
        return b"".join(self.audio_chunks)

    def clear(self) -> None:
        self.chunks = 0
        self.bytes_received = 0
        self.transcript_hints.clear()
        self.audio_chunks.clear()
        self.mime_type = "audio/webm"
