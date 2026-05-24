from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(80), default="Dreamer")
    password_hash: Mapped[str] = mapped_column(String(255))
    learning_vibe: Mapped[str] = mapped_column(String(24), default="Chill")
    active_language_code: Mapped[str] = mapped_column(String(12), default="en")
    native_language_code: Mapped[str] = mapped_column(String(12), default="uk")
    daily_vibe_minutes: Mapped[int] = mapped_column(Integer, default=5)
    ai_tone: Mapped[str] = mapped_column(String(80), default="chill-bro from California")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    words = relationship("Word", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
