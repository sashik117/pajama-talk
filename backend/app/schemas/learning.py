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


class LearningDailyTask(BaseModel):
    id: str
    title: str
    detail: str
    action: str
    phrase: str = ""
    minutes: int = 3


class LearningPathResponse(BaseModel):
    language_code: str
    language_name: str
    level: str
    assistant_role: str
    next_room_prompt: str
    profile_summary: str = ""
    coach_tip: str = ""
    review_prompt: str = ""
    speaking_drill: str = ""
    objectives: list[str] = []
    daily_plan: list[LearningDailyTask] = []
    steps: list[LearningStep]
