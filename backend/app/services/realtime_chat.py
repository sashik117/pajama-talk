from collections.abc import AsyncIterator

from sqlalchemy.orm import Session

from app.domain.chat import UserPresence, active_presence
from app.models.user import User
from app.services.ai_service import stream_roleplay_reply
from app.services.chat_persistence import ChatRepository
from app.services.voice_service import VoiceRealtimeService


class RealtimeChatService:
    """Coordinates chat turns without knowing about WebSocket transport details."""

    def __init__(self, db: Session, user: User, room_id: str) -> None:
        self.db = db
        self.user = user
        self.room_id = room_id
        self.repository = ChatRepository(db)
        self.presence = active_presence(user.id, room_id)
        self.voice = VoiceRealtimeService(language_code=user.active_language_code)

    def user_presence(self) -> UserPresence:
        return self.presence

    def record_user_message(self, content: str) -> None:
        self.repository.save_user_turn(self.user, self.room_id, content)

    async def stream_assistant_reply(self, user_text: str, mood: str = "steady") -> AsyncIterator[str]:
        reply_parts: list[str] = []
        try:
            async for token_text in stream_roleplay_reply(
                room_id=self.room_id,
                user_text=user_text,
                tone=self.user.ai_tone,
                language_code=self.user.active_language_code,
                learning_terms=self.repository.learning_terms(self.user),
                target_language_code=self.user.native_language_code,
                mood=mood,
            ):
                reply_parts.append(token_text)
                yield token_text
        finally:
            reply = "".join(reply_parts).strip()
            if reply:
                self.repository.save_assistant_turn(self.user, self.room_id, reply)

    def call_summary(self) -> dict[str, object]:
        return self.repository.call_summary(self.user, self.room_id)
