from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.languages import normalize_language_code
from app.db.session import get_db
from app.models.user import User
from app.models.word import ReviewGrade, SrsData, Word
from app.schemas.word import ReviewRequest, ReviewResponse, WordCreate, WordEnrichRequest, WordResponse
from app.services.ai_service import enrich_word
from app.services.srs import schedule_review

router = APIRouter(prefix="/words", tags=["words"])


def to_word_response(word: Word) -> WordResponse:
    return WordResponse(
        id=word.id,
        language_code=word.language_code,
        term=word.term,
        translation=word.translation,
        transcription=word.transcription,
        meme=word.meme,
        example_one=word.example_one,
        example_two=word.example_two,
        source_context=word.source_context,
        color_level=word.color_level,
        due_at=word.srs.due_at if word.srs else None,
    )


@router.get("", response_model=list[WordResponse])
def list_words(
    language_code: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[WordResponse]:
    query = db.query(Word).filter(Word.owner_id == user.id)
    if language_code is not None:
        query = query.filter(Word.language_code == normalize_language_code(language_code))
    words = query.order_by(Word.created_at.desc()).all()
    return [to_word_response(word) for word in words]


@router.post("", response_model=WordResponse, status_code=status.HTTP_201_CREATED)
def create_word(
    payload: WordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> WordResponse:
    word = Word(owner_id=user.id, **payload.model_dump())
    word.srs = SrsData()
    db.add(word)
    db.commit()
    db.refresh(word)
    return to_word_response(word)


@router.post("/enrich", response_model=WordResponse, status_code=status.HTTP_201_CREATED)
def enrich_and_create_word(
    payload: WordEnrichRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> WordResponse:
    enriched = enrich_word(
        term=payload.term,
        source_context=payload.source_context,
        target_language=payload.target_language,
        language_code=payload.language_code,
    )
    word = Word(owner_id=user.id, **enriched.model_dump())
    word.srs = SrsData()
    db.add(word)
    db.commit()
    db.refresh(word)
    return to_word_response(word)


@router.post("/{word_id}/review", response_model=ReviewResponse)
def review_word(
    word_id: int,
    payload: ReviewRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ReviewResponse:
    word = db.query(Word).filter(Word.id == word_id, Word.owner_id == user.id).first()
    if word is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Word not found.")

    if word.srs is None:
        word.srs = SrsData()

    schedule_review(word.srs, payload.grade)
    if payload.grade == ReviewGrade.REMEMBER:
        word.color_level = min(5, word.color_level + 1)
    else:
        word.color_level = max(0, word.color_level - 1)

    db.commit()
    db.refresh(word.srs)
    return ReviewResponse(
        word_id=word.id,
        grade=payload.grade,
        repetitions=word.srs.repetitions,
        lapses=word.srs.lapses,
        interval_minutes=word.srs.interval_minutes,
        due_at=word.srs.due_at,
        color_level=word.color_level,
    )
