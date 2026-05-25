from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.languages import language_name, normalize_language_code, normalize_native_language_code
from app.core.security import decode_access_token
from app.db.session import SessionLocal, get_db
from app.models.chat import ChatMessage
from app.models.user import User
from app.models.word import Word
from app.schemas.speaking import EchoRequest, EchoResponse, SpeakingHintsRequest, SpeakingHintsResponse, SpeakingRoom
from app.services.ai_service import generate_speaking_hints, stream_roleplay_reply
from app.services.grammar import detect_mistake_tag
from app.services.language_course import starter_pack
from app.services.pronunciation_service import echo_feedback

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
    SpeakingRoom(
        id="market-mia",
        title="Tiny Market",
        character="Mia",
        vibe="patient shop assistant",
        prompt="You need to buy something and ask for the price politely.",
        accent_color="#FFD982",
    ),
    SpeakingRoom(
        id="doctor-lee",
        title="Clinic Visit",
        character="Dr. Lee",
        vibe="calm doctor with simple questions",
        prompt="You explain how you feel and answer basic health questions.",
        accent_color="#B7DDE8",
    ),
    SpeakingRoom(
        id="street-ivy",
        title="City Directions",
        character="Ivy",
        vibe="helpful local guide",
        prompt="You are lost in a new city and need simple directions.",
        accent_color="#D8E7A6",
    ),
    SpeakingRoom(
        id="date-luna",
        title="Park Date",
        character="Luna",
        vibe="warm casual small talk",
        prompt="You practice light, natural small talk during a walk.",
        accent_color="#F5C7D6",
    ),
    SpeakingRoom(
        id="campus-tom",
        title="First Class",
        character="Tom",
        vibe="friendly classmate",
        prompt="You introduce yourself and ask about a lesson or schedule.",
        accent_color="#C7D7FF",
    ),
]

ROOM_PROMPT_COPY = {
    "uk": "AI-вчитель для {name}. Почни коротко: {hello} Потім спробуй: {want}",
    "ru": "AI-учитель для {name}. Начни коротко: {hello} Потом попробуй: {want}",
    "en": "AI teacher for {name}. Start short: {hello} Then try: {want}",
}


@router.get("/rooms", response_model=list[SpeakingRoom])
def speaking_rooms(
    language_code: str | None = Query(default=None),
    target_language_code: str | None = Query(default=None),
    user: User = Depends(get_current_user),
) -> list[SpeakingRoom]:
    code = normalize_language_code(language_code or user.active_language_code)
    target_code = normalize_native_language_code(target_language_code or user.native_language_code)
    name = language_name(code)
    pack = starter_pack(code)
    copy = ROOM_PROMPT_COPY.get(target_code, ROOM_PROMPT_COPY["en"])
    return [
        room.model_copy(
            update={
                "prompt": copy.format(name=name, hello=pack["hello"][0], want=pack["want"][0])
            },
        )
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


@router.post("/echo", response_model=EchoResponse)
def speaking_echo(
    payload: EchoRequest,
    user: User = Depends(get_current_user),
) -> EchoResponse:
    return echo_feedback(payload.phrase, payload.transcript, user.native_language_code)


def _learning_terms(db: Session, user: User) -> list[str]:
    return [
        row[0]
        for row in (
            db.query(Word.term)
            .filter(
                Word.owner_id == user.id,
                Word.language_code == user.active_language_code,
                Word.status == "learning",
            )
            .order_by(Word.created_at.desc())
            .limit(6)
            .all()
        )
    ]


async def _stream_assistant_reply(
    websocket: WebSocket,
    db: Session,
    user: User,
    room_id: str,
    message: str,
    token_type: str,
    mood: str = "steady",
) -> str:
    reply_parts: list[str] = []
    async for token_text in stream_roleplay_reply(
        room_id=room_id,
        user_text=message,
        tone=user.ai_tone,
        language_code=user.active_language_code,
        learning_terms=_learning_terms(db, user),
        target_language_code=user.native_language_code,
        mood=mood,
    ):
        reply_parts.append(token_text)
        await websocket.send_json({"type": token_type, "value": token_text})

    reply = "".join(reply_parts).strip()
    db.add(ChatMessage(owner_id=user.id, room_id=room_id, role="assistant", content=reply))
    db.commit()
    return reply


def _call_summary(db: Session, user: User, room_id: str) -> dict[str, object]:
    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.owner_id == user.id, ChatMessage.room_id == room_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(16)
        .all()
    )
    ordered = list(reversed(history))
    user_turns = [item for item in ordered if item.role == "user"]
    assistant_text = " ".join(item.content for item in ordered if item.role == "assistant")
    phrases = []
    for chunk in assistant_text.replace("?", ".").replace("!", ".").split("."):
        phrase = chunk.strip()
        if 8 <= len(phrase) <= 48 and phrase not in phrases:
            phrases.append(phrase)
        if len(phrases) == 4:
            break
    mistakes = [item.mistake_tag for item in ordered if item.mistake_tag]
    grammar_feedback = (
        f"Focus next time: {mistakes[-1].replace('_', ' ')}."
        if mistakes
        else "No repeated grammar pattern yet. Keep speaking in short, clear sentences."
    )
    return {
        "topic": f"{len(user_turns)} voice turns in {room_id.replace('-', ' ')}.",
        "new_phrases": phrases or ["Could I say that another way?", "What would you recommend next?"],
        "grammar_feedback": grammar_feedback,
        "turns": len(user_turns),
    }


def _user_from_ws_token(websocket: WebSocket, db: Session) -> User | None:
    token = websocket.query_params.get("token")
    if token is None:
        return None
    try:
        subject = decode_access_token(token)
    except Exception:
        return None
    return db.query(User).filter(User.email == subject).first()


@router.websocket("/ws")
async def speaking_ws(websocket: WebSocket) -> None:
    room_id = websocket.query_params.get("room_id", "coffee-alex")
    mood = websocket.query_params.get("mood", "steady")
    db: Session = SessionLocal()
    user = _user_from_ws_token(websocket, db)
    if user is None:
        db.close()
        await websocket.close(code=4401)
        return

    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            db.add(
                ChatMessage(
                    owner_id=user.id,
                    room_id=room_id,
                    role="user",
                    content=message,
                    mistake_tag=detect_mistake_tag(message),
                )
            )
            db.commit()

            await _stream_assistant_reply(websocket, db, user, room_id, message, "token", mood=mood)
            await websocket.send_json({"type": "done"})
    except WebSocketDisconnect:
        return
    finally:
        db.close()


@router.websocket("/voice-ws")
async def speaking_voice_ws(websocket: WebSocket) -> None:
    room_id = websocket.query_params.get("room_id", "coffee-alex")
    mood = websocket.query_params.get("mood", "steady")
    db: Session = SessionLocal()
    user = _user_from_ws_token(websocket, db)
    if user is None:
        db.close()
        await websocket.close(code=4401)
        return

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
                await websocket.send_json({"type": "call_summary", "value": _call_summary(db, user, room_id)})
                await websocket.send_json({"type": "done"})
                continue

            message = str(payload.get("value") or payload.get("text") or "").strip()
            if not message:
                await websocket.send_json({"type": "error", "value": "Empty voice turn."})
                continue

            db.add(
                ChatMessage(
                    owner_id=user.id,
                    room_id=room_id,
                    role="user",
                    content=message,
                    mistake_tag=detect_mistake_tag(message),
                )
            )
            db.commit()
            await websocket.send_json({"type": "transcript", "value": message})
            reply = await _stream_assistant_reply(websocket, db, user, room_id, message, "assistant_token", mood=mood)
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
