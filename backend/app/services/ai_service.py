from collections.abc import AsyncIterator
import asyncio
import re

from app.schemas.context import ContextAnalyzeResponse, ContextHighlight
from app.schemas.word import WordCreate


def enrich_word(term: str, source_context: str = "", target_language: str = "Ukrainian") -> WordCreate:
    clean_term = term.strip()
    translation = _mock_translate(clean_term, target_language)
    return WordCreate(
        term=clean_term,
        translation=translation,
        transcription=f"/{clean_term.lower()}/",
        meme=f"When '{clean_term}' enters the chat and suddenly the sentence has main-character energy.",
        example_one=f"I keep seeing '{clean_term}' in real conversations, so it is worth saving.",
        example_two=f"That moment felt very '{clean_term}', but in the best possible way.",
        source_context=source_context,
    )


def analyze_context(text: str, target_language: str = "Ukrainian") -> ContextAnalyzeResponse:
    words = [word.lower() for word in re.findall(r"[A-Za-z][A-Za-z'-]{2,}", text)]
    unique_words = list(dict.fromkeys(words))[:8]
    highlights = [
        ContextHighlight(
            phrase=word,
            explanation=f"Ймовірно важливе слово у цьому контексті. Додай його, якщо воно чіпляє.",
            addable_words=[word],
        )
        for word in unique_words[:3]
    ]
    return ContextAnalyzeResponse(
        summary="Текст виглядає як живий шматок мови, не підручниковий приклад.",
        hidden_meaning="Тут важливі не лише слова, а тон: він звучить розмовно, трохи емоційно і дуже контекстно.",
        highlights=highlights,
        suggested_words=unique_words,
    )


async def stream_roleplay_reply(room_id: str, user_text: str, tone: str) -> AsyncIterator[str]:
    reply = _roleplay_reply(room_id, user_text, tone)
    for word in reply.split(" "):
        await asyncio.sleep(0.03)
        yield word + " "


def _roleplay_reply(room_id: str, user_text: str, tone: str) -> str:
    if "coffee" in room_id:
        return "Nice choice. Want it iced, hot, or emotionally supportive with oat milk?"
    if "airport" in room_id:
        return "No panic. Show me your boarding pass and we will find the right gate together."
    if "interview" in room_id:
        return "Good start. Try adding one concrete result, like performance, users, or a bug you fixed."
    return f"I hear you. In my {tone} mode, I would answer a little softer and keep the conversation moving."


def _mock_translate(term: str, target_language: str) -> str:
    dictionary = {
        "cozy": "затишний",
        "awkward": "незручний",
        "deadline": "дедлайн",
        "crush": "краш",
        "vibe": "вайб",
    }
    return dictionary.get(term.lower(), f"{term} ({target_language})")
