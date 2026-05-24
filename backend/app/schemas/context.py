from pydantic import BaseModel, Field


class ContextAnalyzeRequest(BaseModel):
    text: str = Field(min_length=3, max_length=4000)
    target_language: str = "Ukrainian"


class ContextHighlight(BaseModel):
    phrase: str
    explanation: str
    addable_words: list[str]


class ContextAnalyzeResponse(BaseModel):
    summary: str
    hidden_meaning: str
    highlights: list[ContextHighlight]
    suggested_words: list[str]
