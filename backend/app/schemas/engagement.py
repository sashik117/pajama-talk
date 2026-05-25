from pydantic import BaseModel


class OracleIdiom(BaseModel):
    phrase: str
    explanation: str


class OracleResponse(BaseModel):
    language_code: str
    prediction: str
    idioms: list[OracleIdiom]


class SlangResponse(BaseModel):
    language_code: str
    term: str
    meaning: str
    example: str
    source_note: str


class MemePuzzleResponse(BaseModel):
    language_code: str
    prompt: str
    template: str
    pieces: list[str]
    answer: str
    target_word: str
