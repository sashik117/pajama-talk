from collections.abc import AsyncIterator
import asyncio
import re

from app.core.languages import language_name, normalize_language_code
from app.schemas.context import ContextAnalyzeResponse, ContextHighlight
from app.schemas.word import WordCreate
from app.services.ai_prompts import context_analysis_prompt, word_enrichment_prompt
from app.services.ai_provider import get_ai_provider


def enrich_word(
    term: str,
    source_context: str = "",
    target_language: str = "Ukrainian",
    language_code: str = "en",
) -> WordCreate:
    clean_term = term.strip()
    normalized_code = normalize_language_code(language_code)
    ai_payload = get_ai_provider().generate_json(
        word_enrichment_prompt(clean_term, source_context, normalized_code, target_language),
    )
    if ai_payload:
        return WordCreate(
            term=clean_term,
            language_code=normalized_code,
            translation=str(ai_payload.get("translation", "")),
            transcription=str(ai_payload.get("transcription", "")),
            meme=str(ai_payload.get("meme", "")),
            example_one=str(ai_payload.get("example_one", "")),
            example_two=str(ai_payload.get("example_two", "")),
            source_context=source_context,
        )

    source_language = language_name(language_code)
    translation = _mock_translate(clean_term, target_language)
    return WordCreate(
        term=clean_term,
        language_code=normalized_code,
        translation=translation,
        transcription=f"/{clean_term.lower()}/",
        meme=f"When '{clean_term}' enters the {source_language} chat and suddenly the sentence has main-character energy.",
        example_one=f"I keep seeing '{clean_term}' in {source_language} conversations, so it is worth saving.",
        example_two=f"That {source_language} moment felt very '{clean_term}', but in the best possible way.",
        source_context=source_context,
    )


def analyze_context(
    text: str,
    target_language: str = "Ukrainian",
    language_code: str = "en",
) -> ContextAnalyzeResponse:
    normalized_code = normalize_language_code(language_code)
    ai_payload = get_ai_provider().generate_json(
        context_analysis_prompt(text, normalized_code, target_language),
    )
    if ai_payload:
        highlights = [
            ContextHighlight(
                phrase=str(item.get("phrase", "")),
                explanation=str(item.get("explanation", "")),
                addable_words=[str(word) for word in item.get("addable_words", [])][:4],
            )
            for item in ai_payload.get("highlights", [])[:6]
            if isinstance(item, dict)
        ]
        return ContextAnalyzeResponse(
            summary=str(ai_payload.get("summary", "")),
            hidden_meaning=str(ai_payload.get("hidden_meaning", "")),
            highlights=highlights,
            suggested_words=[str(word) for word in ai_payload.get("suggested_words", [])][:12],
        )

    source_language = language_name(language_code)
    words = [
        word.lower()
        for word in re.findall(r"[^\W\d_][^\W\d_'-]*", text, flags=re.UNICODE)
        if len(word.strip()) >= 2
    ]
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
        summary=f"Це схоже на живий шматок {source_language}, не підручниковий приклад.",
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
        "ahoj": "привіт",
        "spoko": "окей / спокійно",
        "pohoda": "спокій / норм",
        "coucou": "привітулі",
        "vale": "добре / окей",
        "allora": "ну / отже",
        "merhaba": "привіт",
    }
    return dictionary.get(term.lower(), f"{term} ({target_language})")
