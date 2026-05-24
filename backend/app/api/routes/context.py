from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.context import ContextAnalyzeRequest, ContextAnalyzeResponse
from app.services.ai_service import analyze_context

router = APIRouter(prefix="/context", tags=["context"])


@router.post("/analyze", response_model=ContextAnalyzeResponse)
def context_buddy(
    payload: ContextAnalyzeRequest,
    _: User = Depends(get_current_user),
) -> ContextAnalyzeResponse:
    return analyze_context(payload.text, payload.target_language, payload.language_code)
