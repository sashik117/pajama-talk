from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.languages import normalize_language_code, normalize_native_language_code
from app.db.session import get_db
from app.models.user import User
from app.models.word import Word
from app.schemas.engagement import MemePuzzleResponse, OracleResponse, SlangResponse
from app.services.meme_factory import meme_puzzle
from app.services.oracle_service import daily_oracle, slang_wheel

router = APIRouter(prefix="/engagement", tags=["engagement"])


@router.get("/oracle", response_model=OracleResponse)
def oracle(
    language_code: str | None = Query(default=None),
    target_language_code: str | None = Query(default=None),
    user: User = Depends(get_current_user),
) -> OracleResponse:
    return daily_oracle(
        user_id=user.id,
        language_code=normalize_language_code(language_code or user.active_language_code),
        target_language_code=normalize_native_language_code(target_language_code or user.native_language_code),
    )


@router.get("/slang", response_model=SlangResponse)
def slang(
    language_code: str | None = Query(default=None),
    user: User = Depends(get_current_user),
) -> SlangResponse:
    return slang_wheel(normalize_language_code(language_code or user.active_language_code))


@router.get("/meme-puzzle", response_model=MemePuzzleResponse)
def meme(
    language_code: str | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemePuzzleResponse:
    code = normalize_language_code(language_code or user.active_language_code)
    terms = [
        row[0]
        for row in (
            db.query(Word.term)
            .filter(Word.owner_id == user.id, Word.language_code == code, Word.status == "learning")
            .order_by(Word.created_at.desc())
            .limit(6)
            .all()
        )
    ]
    return meme_puzzle(terms, code)
