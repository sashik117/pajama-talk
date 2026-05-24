from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.languages import language_name, normalize_language_code
from app.core.security import decode_access_token
from app.db.session import SessionLocal, get_db
from app.models.chat import ChatMessage
from app.models.user import User
from app.schemas.speaking import SpeakingHintsRequest, SpeakingHintsResponse, SpeakingRoom
from app.services.ai_service import generate_speaking_hints, stream_roleplay_reply

router = APIRouter(prefix="/speaking", tags=["speaking"])

ROOMS = [
    SpeakingRoom(
        id="coffee-alex",
        title="Lo-fi Coffee",
        character="Alex",
        vibe="barista with soft sarcasm",
        prompt="You are ordering coffee from a kind hipster barista.",
        accent_color="#F3B6A8",
    ),
    SpeakingRoom(
        id="airport-nova",
        title="Gate B12",
        character="Nova",
        vibe="calm airport helper",
        prompt="You need to solve a boarding gate mix-up.",
        accent_color="#9DCEC0",
    ),
    SpeakingRoom(
        id="interview-jules",
        title="IT Interview",
        character="Jules",
        vibe="friendly tech lead",
        prompt="You are explaining a project during an English interview.",
        accent_color="#C7B8EA",
    ),
]


@router.get("/rooms", response_model=list[SpeakingRoom])
def speaking_rooms(
    language_code: str | None = Query(default=None),
    _: User = Depends(get_current_user),
) -> list[SpeakingRoom]:
    code = normalize_language_code(language_code)
    name = language_name(code)
    return [
        room.model_copy(update={"prompt": f"{room.prompt} Keep the practice in {name}."})
        for room in ROOMS
    ]


@router.post("/hints", response_model=SpeakingHintsResponse)
def speaking_hints(
    payload: SpeakingHintsRequest,
    user: User = Depends(get_current_user),
) -> SpeakingHintsResponse:
    room = next((room for room in ROOMS if room.id == payload.room_id), ROOMS[0])
    return generate_speaking_hints(
        room_prompt=room.prompt,
        last_message=payload.last_message,
        language_code=payload.language_code,
        target_language=language_name(user.native_language_code),
    )


@router.websocket("/ws")
async def speaking_ws(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token")
    room_id = websocket.query_params.get("room_id", "coffee-alex")
    if token is None:
        await websocket.close(code=4401)
        return

    try:
        subject = decode_access_token(token)
    except Exception:
        await websocket.close(code=4401)
        return

    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == subject).first()
    if user is None:
        db.close()
        await websocket.close(code=4401)
        return

    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            db.add(ChatMessage(owner_id=user.id, room_id=room_id, role="user", content=message))
            db.commit()

            reply_parts: list[str] = []
            async for token_text in stream_roleplay_reply(room_id=room_id, user_text=message, tone=user.ai_tone):
                reply_parts.append(token_text)
                await websocket.send_json({"type": "token", "value": token_text})

            reply = "".join(reply_parts).strip()
            db.add(ChatMessage(owner_id=user.id, room_id=room_id, role="assistant", content=reply))
            db.commit()
            await websocket.send_json({"type": "done"})
    except WebSocketDisconnect:
        return
    finally:
        db.close()
