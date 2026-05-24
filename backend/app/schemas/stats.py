from pydantic import BaseModel


class ProfileStatsResponse(BaseModel):
    active_language_code: str
    total_words: int
    language_words: int
    learned_words: int
    due_reviews: int
    daily_vibe_minutes: int
    learning_vibe: str
    ai_tone: str
