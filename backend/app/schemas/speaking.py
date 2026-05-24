from pydantic import BaseModel


class SpeakingRoom(BaseModel):
    id: str
    title: str
    character: str
    vibe: str
    prompt: str
    accent_color: str
