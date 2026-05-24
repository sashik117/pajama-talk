from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ReviewGrade(StrEnum):
    REMEMBER = "remember"
    FORGOT = "forgot"


class Word(Base):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    language_code: Mapped[str] = mapped_column(String(12), default="en", index=True)
    term: Mapped[str] = mapped_column(String(120), index=True)
    translation: Mapped[str] = mapped_column(String(255), default="")
    transcription: Mapped[str] = mapped_column(String(120), default="")
    meme: Mapped[str] = mapped_column(Text, default="")
    example_one: Mapped[str] = mapped_column(Text, default="")
    example_two: Mapped[str] = mapped_column(Text, default="")
    source_context: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(24), default="learning", index=True)
    color_level: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    user = relationship("User", back_populates="words")
    srs = relationship("SrsData", back_populates="word", uselist=False, cascade="all, delete-orphan")


class SrsData(Base):
    __tablename__ = "srs_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id", ondelete="CASCADE"), unique=True)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    lapses: Mapped[int] = mapped_column(Integer, default=0)
    interval_minutes: Mapped[int] = mapped_column(Integer, default=10)
    ease_factor: Mapped[int] = mapped_column(Integer, default=250)
    due_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    last_grade: Mapped[ReviewGrade | None] = mapped_column(Enum(ReviewGrade), nullable=True)

    word = relationship("Word", back_populates="srs")
