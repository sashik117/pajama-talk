from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.chat import ChatMessage
from app.models.user import User
from app.schemas.grammar import GrammarDrop

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

    if "past_simple_vs_present_perfect" not in tags:
        return [
            GrammarDrop(
                id="soft-past-simple",
                title="Past Simple",
                nudge="Йоу, Past Simple сьогодні тихенько проситься на 30 секунд.",
                tiny_explanation="Якщо час закінчився і ти знаєш коли, англійська майже завжди тягнеться до Past Simple.",
                quests=[
                    "I watched it yesterday",
                    "She called me last night",
                    "We met in 2024",
                ],
            )
        ]

    return [
        GrammarDrop(
            id="present-perfect-rescue",
            title="Perfect Rescue",
            nudge="Present Perfect трохи бунтує. Розберемо без драми?",
            tiny_explanation="Коли важливий результат зараз, а не точний момент у минулому, ставимо have або has плюс третю форму.",
            quests=[
                "I have already seen it",
                "She has lost her keys",
                "They have just arrived",
            ],
        )
    ]
