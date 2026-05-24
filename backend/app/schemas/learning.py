from pydantic import BaseModel


class LearningPhrase(BaseModel):
    phrase: str
    pronunciation: str = ""
    meaning: str


class LearningStep(BaseModel):
    id: str
    title: str
    goal: str
    teacher_note: str
    micro_task: str
    examples: list[LearningPhrase]


class LearningPathResponse(BaseModel):
    language_code: str
    language_name: str
    level: str
    assistant_role: str
    next_room_prompt: str
    steps: list[LearningStep]
