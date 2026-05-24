from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.chat import ChatMessage
from app.models.user import User
from app.schemas.grammar import GrammarDrop
from app.services.grammar import drops_for_tags

router = APIRouter(prefix="/grammar", tags=["grammar"])


@router.get("/drops", response_model=list[GrammarDrop])
def grammar_drops(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[GrammarDrop]:
    recent_mistakes = (
        db.query(ChatMessage.mistake_tag)
        .filter(ChatMessage.owner_id == user.id, ChatMessage.mistake_tag.isnot(None))
        .order_by(ChatMessage.created_at.desc())
        .limit(10)
        .all()
    )
    tags = {row[0] for row in recent_mistakes}
    return drops_for_tags(tags)
