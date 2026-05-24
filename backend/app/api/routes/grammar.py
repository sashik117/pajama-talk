from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.chat import ChatMessage
from app.models.user import User
from app.schemas.grammar import GrammarCheckRequest, GrammarCheckResponse, GrammarDrop, GrammarTopic
from app.services.grammar import check_grammar_answer, drops_for_tags, grammar_topics_for_tags

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


@router.get("/topics", response_model=list[GrammarTopic])
def grammar_topics(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[GrammarTopic]:
    recent_mistakes = (
        db.query(ChatMessage.mistake_tag)
        .filter(ChatMessage.owner_id == user.id, ChatMessage.mistake_tag.isnot(None))
        .order_by(ChatMessage.created_at.desc())
        .limit(20)
        .all()
    )
    tags = {row[0] for row in recent_mistakes}
    return grammar_topics_for_tags(tags)


@router.post("/check", response_model=GrammarCheckResponse)
def grammar_check(
    payload: GrammarCheckRequest,
    _: User = Depends(get_current_user),
) -> GrammarCheckResponse:
    return check_grammar_answer(payload.topic_id, payload.exercise_id, payload.answer)
