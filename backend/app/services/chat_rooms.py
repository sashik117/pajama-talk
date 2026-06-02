from app.core.languages import language_name, normalize_language_code, normalize_native_language_code
from app.domain.chat import ChatRoom
from app.models.user import User
from app.schemas.speaking import SpeakingRoom
from app.services.language_course import starter_pack


ROOMS: tuple[ChatRoom, ...] = (
    ChatRoom(
        id="coffee-alex",
        title="Lo-fi Coffee",
        character="Alex",
        vibe="barista with soft sarcasm",
        prompt="You are ordering coffee from a kind hipster barista.",
        accent_color="#F3B6A8",
    ),
    ChatRoom(
        id="airport-nova",
        title="Gate B12",
        character="Nova",
        vibe="calm airport helper",
        prompt="You need to solve a boarding gate mix-up.",
        accent_color="#9DCEC0",
    ),
    ChatRoom(
        id="interview-jules",
        title="IT Interview",
        character="Jules",
        vibe="friendly tech lead",
        prompt="You are explaining a project during an English interview.",
        accent_color="#C7B8EA",
    ),
    ChatRoom(
        id="market-mia",
        title="Tiny Market",
        character="Mia",
        vibe="patient shop assistant",
        prompt="You need to buy something and ask for the price politely.",
        accent_color="#FFD982",
    ),
    ChatRoom(
        id="doctor-lee",
        title="Clinic Visit",
        character="Dr. Lee",
        vibe="calm doctor with simple questions",
        prompt="You explain how you feel and answer basic health questions.",
        accent_color="#B7DDE8",
    ),
    ChatRoom(
        id="street-ivy",
        title="City Directions",
        character="Ivy",
        vibe="helpful local guide",
        prompt="You are lost in a new city and need simple directions.",
        accent_color="#D8E7A6",
    ),
    ChatRoom(
        id="date-luna",
        title="Park Date",
        character="Luna",
        vibe="warm casual small talk",
        prompt="You practice light, natural small talk during a walk.",
        accent_color="#F5C7D6",
    ),
    ChatRoom(
        id="campus-tom",
        title="First Class",
        character="Tom",
        vibe="friendly classmate",
        prompt="You introduce yourself and ask about a lesson or schedule.",
        accent_color="#C7D7FF",
    ),
)

ROOM_PROMPT_COPY = {
    "uk": "AI-вчитель для {name}. Почни коротко: {hello} Потім спробуй: {want}",
    "ru": "AI-учитель для {name}. Начни коротко: {hello} Потом попробуй: {want}",
    "en": "AI teacher for {name}. Start short: {hello} Then try: {want}",
}


def room_by_id(room_id: str) -> ChatRoom:
    return next((room for room in ROOMS if room.id == room_id), ROOMS[0])


def speaking_rooms_for_user(user: User, language_code: str | None = None, target_language_code: str | None = None) -> list[SpeakingRoom]:
    code = normalize_language_code(language_code or user.active_language_code)
    target_code = normalize_native_language_code(target_language_code or user.native_language_code)
    name = language_name(code)
    pack = starter_pack(code)
    copy = ROOM_PROMPT_COPY.get(target_code, ROOM_PROMPT_COPY["en"])
    prompt = copy.format(name=name, hello=pack["hello"][0], want=pack["want"][0])
    return [
        SpeakingRoom(
            id=room.id,
            title=room.title,
            character=room.character,
            vibe=room.vibe,
            prompt=prompt,
            accent_color=room.accent_color,
        )
        for room in ROOMS
    ]
