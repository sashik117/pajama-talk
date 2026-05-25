from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user
from app.core.languages import normalize_language_code, normalize_native_language_code
from app.models.user import User
from app.schemas.learning import LearningPathResponse
from app.services.language_course import build_learning_path

router = APIRouter(prefix="/learning", tags=["learning"])


@router.get("/path", response_model=LearningPathResponse)
def learning_path(
    language_code: str | None = Query(default=None),
    target_language_code: str | None = Query(default=None),
    user: User = Depends(get_current_user),
) -> LearningPathResponse:
    code = normalize_language_code(language_code or user.active_language_code)
    explanation_code = normalize_native_language_code(target_language_code or user.native_language_code)
    return build_learning_path(
        code,
        explanation_code,
        current_level=user.current_level,
        target_level=user.target_level,
        effort_level=user.effort_level,
    )
