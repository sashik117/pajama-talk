from pydantic import BaseModel, Field, field_validator

from app.core.languages import normalize_language_code


class ContextAnalyzeRequest(BaseModel):
    text: str = Field(min_length=3, max_length=4000)
    language_code: str = "en"
    target_language: str = "Ukrainian"

    @field_validator("language_code")
    @classmethod
    def validate_language_code(cls, value: str) -> str:
        return normalize_language_code(value)


class ContextHighlight(BaseModel):
    phrase: str
    explanation: str
    addable_words: list[str]


class ContextAnalyzeResponse(BaseModel):
    summary: str
    hidden_meaning: str
    highlights: list[ContextHighlight]
    suggested_words: list[str]
