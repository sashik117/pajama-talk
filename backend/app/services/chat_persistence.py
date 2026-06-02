from sqlalchemy.orm import Session

from app.domain.chat import Message
from app.models.chat import ChatMessage
from app.models.user import User
from app.models.word import Word
from app.services.grammar import detect_mistake_tag


class ChatRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save_user_turn(self, user: User, room_id: str, content: str) -> Message:
        message = Message(room_id=room_id, role="user", content=content, mistake_tag=detect_mistake_tag(content))
        self.db.add(
            ChatMessage(
                owner_id=user.id,
                room_id=message.room_id,
                role=message.role,
                content=message.content,
                mistake_tag=message.mistake_tag,
            )
        )
        self.db.commit()
        return message

    def save_assistant_turn(self, user: User, room_id: str, content: str) -> Message:
        message = Message(room_id=room_id, role="assistant", content=content)
        self.db.add(ChatMessage(owner_id=user.id, room_id=room_id, role=message.role, content=message.content))
        self.db.commit()
        return message

    def learning_terms(self, user: User, limit: int = 6) -> list[str]:
        return [
            row[0]
            for row in (
                self.db.query(Word.term)
                .filter(
                    Word.owner_id == user.id,
                    Word.language_code == user.active_language_code,
                    Word.status == "learning",
                )
                .order_by(Word.created_at.desc())
                .limit(limit)
                .all()
            )
        ]

    def recent_history(self, user: User, room_id: str, limit: int = 16) -> list[ChatMessage]:
        return list(
            reversed(
                self.db.query(ChatMessage)
                .filter(ChatMessage.owner_id == user.id, ChatMessage.room_id == room_id)
                .order_by(ChatMessage.created_at.desc())
                .limit(limit)
                .all()
            )
        )

    def call_summary(self, user: User, room_id: str) -> dict[str, object]:
        history = self.recent_history(user, room_id)
        user_turns = [item for item in history if item.role == "user"]
        assistant_text = " ".join(item.content for item in history if item.role == "assistant")
        phrases: list[str] = []
        for chunk in assistant_text.replace("?", ".").replace("!", ".").split("."):
            phrase = chunk.strip()
            if 8 <= len(phrase) <= 48 and phrase not in phrases:
                phrases.append(phrase)
            if len(phrases) == 4:
                break
        mistakes = [item.mistake_tag for item in history if item.mistake_tag]
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
