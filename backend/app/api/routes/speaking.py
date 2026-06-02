from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.languages import language_name
from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.speaking import EchoRequest, EchoResponse, SpeakingHintsRequest, SpeakingHintsResponse, SpeakingRoom
from app.services.ai_service import generate_speaking_hints
from app.services.chat_rooms import room_by_id, speaking_rooms_for_user
from app.services.pronunciation_service import echo_feedback
from app.services.realtime_chat import RealtimeChatService

router = APIRouter(prefix="/speaking", tags=["speaking"])


@router.get("/rooms", response_model=list[SpeakingRoom])
def speaking_rooms(
    language_code: str | None = Query(default=None),
    target_language_code: str | None = Query(default=None),
    user: User = Depends(get_current_user),
) -> list[SpeakingRoom]:
    return speaking_rooms_for_user(user, language_code, target_language_code)


@router.post("/hints", response_model=SpeakingHintsResponse)
def speaking_hints(
    payload: SpeakingHintsRequest,
    user: User = Depends(get_current_user),
) -> SpeakingHintsResponse:
    room = room_by_id(payload.room_id)
    return generate_speaking_hints(
        room_prompt=room.prompt,
        last_message=payload.last_message,
        language_code=payload.language_code,
        target_language=language_name(user.native_language_code),
    )


@router.post("/echo", response_model=EchoResponse)
def speaking_echo(
    payload: EchoRequest,
    user: User = Depends(get_current_user),
) -> EchoResponse:
    return echo_feedback(payload.phrase, payload.transcript, user.native_language_code)


def _user_from_ws_token(websocket: WebSocket, db: Session) -> User | None:
    token = websocket.query_params.get("token")
    if token is None:
        return None
    try:
        subject = decode_access_token(token)
    except Exception:
        return None
    return db.query(User).filter(User.email == subject).first()


async def _open_realtime_session(websocket: WebSocket) -> tuple[Session, User, RealtimeChatService] | None:
    room_id = websocket.query_params.get("room_id", "coffee-alex")
    db: Session = SessionLocal()
    user = _user_from_ws_token(websocket, db)
    if user is None:
        db.close()
        await websocket.close(code=4401)
        return None
    return db, user, RealtimeChatService(db, user, room_id)


async def _send_assistant_stream(websocket: WebSocket, service: RealtimeChatService, message: str, token_type: str, mood: str) -> str:
    reply_parts: list[str] = []
    async for token_text in service.stream_assistant_reply(message, mood=mood):
        reply_parts.append(token_text)
        await websocket.send_json({"type": token_type, "value": token_text})
    return "".join(reply_parts).strip()


@router.websocket("/ws")
async def speaking_ws(websocket: WebSocket) -> None:
    session = await _open_realtime_session(websocket)
    if session is None:
        return

    db, _user, service = session
    mood = websocket.query_params.get("mood", "steady")
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            service.record_user_message(message)
            await _send_assistant_stream(websocket, service, message, "token", mood)
            await websocket.send_json({"type": "done"})
    except WebSocketDisconnect:
        return
    finally:
        db.close()


@router.websocket("/voice-ws")
async def speaking_voice_ws(websocket: WebSocket) -> None:
    session = await _open_realtime_session(websocket)
    if session is None:
        return

    db, _user, service = session
    mood = websocket.query_params.get("mood", "steady")
    await websocket.accept()
    await websocket.send_json(
        {
            "type": "session_ready",
            "stt": "browser-stt-now; whisper-audio-chunks-ready",
            "tts": "client-speech-synthesis-now; provider-audio-chunks-ready",
        }
    )
    try:
        while True:
            payload = await websocket.receive_json()
            event_type = payload.get("type")
            if event_type == "audio_chunk":
                await websocket.send_json({"type": "stt_status", "value": "audio chunk accepted"})
                continue
            if event_type == "end_call":
                await websocket.send_json({"type": "call_summary", "value": service.call_summary()})
                await websocket.send_json({"type": "done"})
                continue

            message = str(payload.get("value") or payload.get("text") or "").strip()
            if not message:
                await websocket.send_json({"type": "error", "value": "Empty voice turn."})
                continue

            service.record_user_message(message)
            await websocket.send_json({"type": "transcript", "value": message})
            reply = await _send_assistant_stream(websocket, service, message, "assistant_token", mood)
            await websocket.send_json(
                {
                    "type": "tts",
                    "format": "client_speech_synthesis",
                    "text": reply,
                    "speed": payload.get("speed", 1),
                }
            )
            await websocket.send_json({"type": "done"})
    except WebSocketDisconnect:
        return
    finally:
        db.close()
