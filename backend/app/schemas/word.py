from datetime import datetime

from pydantic import BaseModel, Field

from app.models.word import ReviewGrade


class WordCreate(BaseModel):
    term: str = Field(min_length=1, max_length=120)
    translation: str = ""
    transcription: str = ""
    meme: str = ""
    example_one: str = ""
    example_two: str = ""
    source_context: str = ""


class WordEnrichRequest(BaseModel):
    term: str = Field(min_length=1, max_length=120)
    source_context: str = ""
    target_language: str = "Ukrainian"


class WordResponse(BaseModel):
    id: int
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
