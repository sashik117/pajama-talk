from pydantic import BaseModel, Field, field_validator

from app.core.languages import normalize_language_code


class SpeakingRoom(BaseModel):
    id: str
    title: str
    character: str
    vibe: str
    prompt: str
    accent_color: str


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
