from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.core.languages import normalize_language_code
from app.models.word import ReviewGrade


class WordCreate(BaseModel):
    term: str = Field(min_length=1, max_length=120)
    language_code: str = "en"
    translation: str = ""
    transcription: str = ""
    meme: str = ""
    example_one: str = ""
    example_two: str = ""
    source_context: str = ""

    @field_validator("language_code")
    @classmethod
    def validate_language_code(cls, value: str) -> str:
        return normalize_language_code(value)


class WordEnrichRequest(BaseModel):
    term: str = Field(min_length=1, max_length=120)
    language_code: str = "en"
    source_context: str = ""
    target_language: str = "Ukrainian"

    @field_validator("language_code")
    @classmethod
    def validate_language_code(cls, value: str) -> str:
        return normalize_language_code(value)


class WordResponse(BaseModel):
    id: int
    language_code: str
    term: str
    translation: str
    transcription: str
    meme: str
    example_one: str
    example_two: str
    source_context: str
    color_level: int
    due_at: datetime | None = None


class ReviewRequest(BaseModel):
    grade: ReviewGrade


class ReviewResponse(BaseModel):
    word_id: int
    grade: ReviewGrade
    repetitions: int
    lapses: int
    interval_minutes: int
    due_at: datetime
    color_level: int
