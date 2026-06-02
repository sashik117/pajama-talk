from pydantic import BaseModel, Field, field_validator

from app.core.languages import normalize_language_code


class SpeakingRoom(BaseModel):
    id: str
    title: str
    character: str
    vibe: str
    prompt: str
    accent_color: str


class SpeakingHistoryMessage(BaseModel):
    id: int
    room_id: str
    role: str
    content: str
    created_at: str


class SpeakingHintsRequest(BaseModel):
    room_id: str = Field(min_length=1, max_length=80)
    last_message: str = Field(default="", max_length=1000)
    language_code: str = "en"

    @field_validator("language_code")
    @classmethod
    def validate_language_code(cls, value: str) -> str:
        return normalize_language_code(value)


class SpeakingHintsResponse(BaseModel):
    simple: str
    conversational: str
    spicy: str


class EchoRequest(BaseModel):
    phrase: str = Field(min_length=2, max_length=240)
    transcript: str = Field(default="", max_length=300)
    language_code: str = "en"

    @field_validator("language_code")
    @classmethod
    def validate_echo_language_code(cls, value: str) -> str:
        return normalize_language_code(value)


class EchoResponse(BaseModel):
    score: int
    feedback: str
    next_tip: str
    matched_text: str
