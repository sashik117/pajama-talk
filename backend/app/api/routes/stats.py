from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.word import SrsData, Word
from app.schemas.stats import ProfileStatsResponse

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/me", response_model=ProfileStatsResponse)
def my_stats(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ProfileStatsResponse:
    language_code = user.active_language_code
    total_words = db.query(Word).filter(Word.owner_id == user.id).count()
    language_words_query = db.query(Word).filter(
        Word.owner_id == user.id,
        Word.language_code == language_code,
    )
    language_words = language_words_query.count()
    learned_words = language_words_query.filter(Word.color_level >= 5).count()
    due_reviews = (
        db.query(Word)
        .join(SrsData)
        .filter(
            Word.owner_id == user.id,
            Word.language_code == language_code,
            SrsData.due_at <= datetime.now(UTC),
        )
        .count()
    )

    return ProfileStatsResponse(
        active_language_code=language_code,
        total_words=total_words,
        language_words=language_words,
        learned_words=learned_words,
        due_reviews=due_reviews,
        daily_vibe_minutes=user.daily_vibe_minutes,
        learning_vibe=user.learning_vibe,
        ai_tone=user.ai_tone,
    )
