from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.languages import language_name
from app.core.security import decode_access_token
from app.db.session import SessionLocal, get_db
from app.domain.realtime_events import (
    TokenEventType,
    call_summary_event,
    done_event,
    error_event,
    pong_event,
    session_ready_event,
    status_event,
    token_event,
    transcript_event,
    tts_event,
)
from app.models.user import User
from app.schemas.speaking import EchoRequest, EchoResponse, SpeakingHintsRequest, SpeakingHintsResponse, SpeakingHistoryMessage, SpeakingRoom
from app.services.ai_service import generate_speaking_hints
from app.services.chat_persistence import ChatRepository
from app.services.chat_rooms import room_by_id, speaking_rooms_for_user
from app.services.pronunciation_service import echo_feedback
from app.services.realtime_chat import RealtimeChatService
from app.services.websocket_guard import WS_POLICY_LIMIT_CODE, websocket_connection_limiter

router = APIRouter(prefix="/speaking", tags=["speaking"])

PING_TEXT_EVENTS = {'{"type":"ping"}', '{"type": "ping"}', "__ping__"}


@router.get("/rooms", response_model=list[SpeakingRoom])
def speaking_rooms(
    language_code: str | None = Query(default=None),
    target_language_code: str | None = Query(default=None),
    user: User = Depends(get_current_user),
) -> list[SpeakingRoom]:
    return speaking_rooms_for_user(user, language_code, target_language_code)


@router.get("/history", response_model=list[SpeakingHistoryMessage])
def speaking_history(
    room_id: str = Query(default="coffee-alex", min_length=1, max_length=80),
    limit: int = Query(default=40, ge=1, le=80),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SpeakingHistoryMessage]:
    history = ChatRepository(db).history(user, room_id, limit)
    return [
        SpeakingHistoryMessage(
            id=item.id,
            room_id=item.room_id,
            role=item.role,
            content=item.content,
            created_at=item.created_at.isoformat(),
        )
        for item in history
    ]


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


async def _open_realtime_session(websocket: WebSocket) -> tuple[Session, User, RealtimeChatService, str] | None:
    room_id = websocket.query_params.get("room_id", "coffee-alex")
    db: Session = SessionLocal()
    user = _user_from_ws_token(websocket, db)
    if user is None:
        db.close()
        await websocket.close(code=4401)
        return None
    client_ip = await websocket_connection_limiter.acquire(websocket)
    if client_ip is None:
        db.close()
        await websocket.close(code=WS_POLICY_LIMIT_CODE)
        return None
    return db, user, RealtimeChatService(db, user, room_id), client_ip


async def _send_assistant_stream(websocket: WebSocket, service: RealtimeChatService, message: str, token_type: TokenEventType, mood: str) -> str:
    reply_parts: list[str] = []
    async for token_text in service.stream_assistant_reply(message, mood=mood):
        reply_parts.append(token_text)
        await websocket.send_json(token_event(token_type, token_text))
    return "".join(reply_parts).strip()


async def _send_voice_turn(
    websocket: WebSocket,
    service: RealtimeChatService,
    message: str,
    speed: float | int,
    mood: str,
) -> None:
    service.record_user_message(message)
    await websocket.send_json(transcript_event(message, provider="voice_session", confidence=1.0))
    reply = await _send_assistant_stream(websocket, service, message, "assistant_token", mood)
    speech = service.voice.synthesize_reply(reply, float(speed))
    await websocket.send_json(
        tts_event(
            speech.text,
            speech.speed,
            provider=speech.provider,
            audio_base64=speech.audio_base64,
            mime_type=speech.mime_type,
            audio_format=speech.format,
        )
    )
    await websocket.send_json(done_event())


@router.websocket("/ws")
async def speaking_ws(websocket: WebSocket) -> None:
    session = await _open_realtime_session(websocket)
    if session is None:
        return

    db, _user, service, client_ip = session
    mood = websocket.query_params.get("mood", "steady")
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            if message in PING_TEXT_EVENTS:
                await websocket.send_json(pong_event())
                continue
            service.record_user_message(message)
            await _send_assistant_stream(websocket, service, message, "token", mood)
            await websocket.send_json(done_event())
    except WebSocketDisconnect:
        return
    finally:
        db.close()
        await websocket_connection_limiter.release(client_ip)


@router.websocket("/voice-ws")
async def speaking_voice_ws(websocket: WebSocket) -> None:
    session = await _open_realtime_session(websocket)
    if session is None:
        return

    db, _user, service, client_ip = session
    mood = websocket.query_params.get("mood", "steady")
    await websocket.accept()
    await websocket.send_json(session_ready_event(service.voice.capabilities()))
    try:
        while True:
            payload = await websocket.receive_json()
            event_type = payload.get("type")
            if event_type == "ping":
                await websocket.send_json(pong_event())
                continue
            if event_type == "audio_chunk":
                await websocket.send_json(status_event("audio chunk accepted", service.voice.accept_audio_chunk(payload)))
                continue
            if event_type in {"end_audio", "commit_audio"}:
                transcript = service.voice.transcribe_turn(payload)
                if not transcript.text:
                    await websocket.send_json(error_event("No speech was detected. Try one short sentence."))
                    continue
                service.record_user_message(transcript.text)
                await websocket.send_json(
                    transcript_event(transcript.text, provider=transcript.provider, confidence=transcript.confidence)
                )
                reply = await _send_assistant_stream(websocket, service, transcript.text, "assistant_token", mood)
                speech = service.voice.synthesize_reply(reply, float(payload.get("speed", 1)))
                await websocket.send_json(
                    tts_event(
                        speech.text,
                        speech.speed,
                        provider=speech.provider,
                        audio_base64=speech.audio_base64,
                        mime_type=speech.mime_type,
                        audio_format=speech.format,
                    )
                )
                await websocket.send_json(done_event())
                continue
            if event_type == "end_call":
                await websocket.send_json(call_summary_event(service.call_summary()))
                await websocket.send_json(done_event())
                continue

            message = str(payload.get("value") or payload.get("text") or "").strip()
            if not message:
                await websocket.send_json(error_event("Empty voice turn."))
                continue

            await _send_voice_turn(websocket, service, message, payload.get("speed", 1), mood)
    except WebSocketDisconnect:
        return
    finally:
        db.close()
        await websocket_connection_limiter.release(client_ip)
