from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal


ChatRole = Literal["user", "assistant", "system"]
PresenceState = Literal["connecting", "active", "idle", "left"]


@dataclass(frozen=True)
class ChatRoom:
    id: str
    title: str
    character: str
    vibe: str
    prompt: str
    accent_color: str


@dataclass(frozen=True)
class Message:
    room_id: str
    role: ChatRole
    content: str
    mistake_tag: str | None = None
    created_at: datetime | None = None


@dataclass(frozen=True)
class UserPresence:
    user_id: int
    room_id: str
    state: PresenceState
    last_seen_at: datetime


def active_presence(user_id: int, room_id: str) -> UserPresence:
    return UserPresence(user_id=user_id, room_id=room_id, state="active", last_seen_at=datetime.now(UTC))
