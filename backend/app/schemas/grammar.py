from pydantic import BaseModel


class GrammarDrop(BaseModel):
    id: str
    title: str
    nudge: str
    tiny_explanation: str
    quests: list[str]


class GrammarExample(BaseModel):
    wrong: str | None = None
    right: str
    note: str


class GrammarExercise(BaseModel):
    id: str
    type: str
    prompt: str
    options: list[str] = []
    explanation: str


class GrammarTopic(BaseModel):
    id: str
    tag: str
    title: str
    level: str
    summary: str
    micro_lesson: str
    rules: list[str]
    examples: list[GrammarExample]
    exercises: list[GrammarExercise]
    recommended: bool = False
    reason: str = ""


class GrammarCheckRequest(BaseModel):
    topic_id: str
    exercise_id: str
    answer: str


class GrammarCheckResponse(BaseModel):
    correct: bool
    expected: str
    feedback: str
    score_delta: int
