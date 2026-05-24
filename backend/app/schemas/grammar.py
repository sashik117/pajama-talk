from pydantic import BaseModel


class GrammarDrop(BaseModel):
    id: str
    title: str
    nudge: str
    tiny_explanation: str
    quests: list[str]
