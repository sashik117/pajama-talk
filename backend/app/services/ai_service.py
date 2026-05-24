from collections.abc import AsyncIterator
import asyncio
import re

from app.core.languages import language_name, normalize_language_code
from app.schemas.context import ContextAnalyzeResponse, ContextHighlight
from app.schemas.speaking import SpeakingHintsResponse
from app.schemas.word import WordCreate
from app.services.ai_prompts import context_analysis_prompt, speaking_hints_prompt, word_enrichment_prompt
from app.services.ai_provider import get_ai_provider
from app.services.language_course import starter_pack


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
    pack = starter_pack(normalized_code)
    return WordCreate(
        term=clean_term,
        language_code=normalized_code,
        translation=translation,
        transcription=f"/{clean_term.lower()}/",
        meme=f"Коли '{clean_term}' заходить у {source_language} sentence і все раптом звучить живіше.",
        example_one=f"{pack['hello'][0]} / слово для контексту: {clean_term}",
        example_two=f"{pack['want'][0]} / спробуй додати '{clean_term}' у живу фразу.",
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
            explanation="Ймовірно важливе слово у цьому контексті. Додай його, якщо воно чіпляє.",
            addable_words=[word],
        )
        for word in unique_words[:3]
    ]
    return ContextAnalyzeResponse(
        summary=f"Це схоже на живий шматок {source_language}, не підручниковий приклад.",
        hidden_meaning=(
            "Тут важливі не лише слова, а тон: він звучить розмовно, трохи емоційно "
            "і дуже контекстно."
        ),
        highlights=highlights,
        suggested_words=unique_words,
    )


async def stream_roleplay_reply(
    room_id: str,
    user_text: str,
    tone: str,
    language_code: str = "en",
    learning_terms: list[str] | None = None,
) -> AsyncIterator[str]:
    reply = _roleplay_reply(room_id, user_text, tone, language_code, learning_terms or [])
    for word in reply.split(" "):
        await asyncio.sleep(0.03)
        yield word + " "


def _roleplay_reply(room_id: str, user_text: str, tone: str, language_code: str, learning_terms: list[str]) -> str:
    pack = starter_pack(language_code)
    learning_hook = ""
    if learning_terms:
        term = learning_terms[0]
        learning_hook = f" Спробуй використати '{term}' у відповіді, якщо підходить."

    if language_code != "en":
        if "coffee" in room_id:
            return f"{pack['thanks'][0]} Тепер як teacher: спробуй відповісти фразою '{pack['want'][0]}'.{learning_hook}"
        if "airport" in room_id:
            return f"{pack['question'][0]} Добре для ситуації в аеропорту. Скажи коротко і я продовжу діалог.{learning_hook}"
        if "interview" in room_id:
            return f"{pack['hello'][0]} Почни з представлення, потім додай одну просту фразу про себе.{learning_hook}"
        return f"{pack['question'][0]} Я як teacher підкину опору, а ти відповідай коротко.{learning_hook}"

    if "coffee" in room_id:
        return f"Nice choice. Want it iced, hot, or emotionally supportive with oat milk?{learning_hook}"
    if "airport" in room_id:
        return f"No panic. Show me your boarding pass and we will find the right gate together.{learning_hook}"
    if "interview" in room_id:
        return f"Good start. Try adding one concrete result, like performance, users, or a bug you fixed.{learning_hook}"
    if "market" in room_id:
        return f"Sure. Ask me for the price, size, or a smaller option, and keep it to one clean sentence.{learning_hook}"
    if "doctor" in room_id:
        return f"Tell me one symptom and when it started. Short answers are perfect here.{learning_hook}"
    if "street" in room_id:
        return f"You are close. Ask me where the station is, then repeat the direction back to me.{learning_hook}"
    if "date" in room_id:
        return f"Nice. Ask one easy question back, like what music or coffee they like.{learning_hook}"
    if "campus" in room_id:
        return f"Start with your name, then ask where the class is or what the homework is.{learning_hook}"
    return f"I hear you. In my {tone} mode, I would answer a little softer and keep the conversation moving.{learning_hook}"


def generate_speaking_hints(
    room_prompt: str,
    last_message: str,
    language_code: str,
    target_language: str = "Ukrainian",
) -> SpeakingHintsResponse:
    normalized_code = normalize_language_code(language_code)
    ai_payload = get_ai_provider().generate_json(
        speaking_hints_prompt(room_prompt, last_message, normalized_code, target_language),
    )
    if ai_payload:
        return SpeakingHintsResponse(
            simple=str(ai_payload.get("simple", "")),
            conversational=str(ai_payload.get("conversational", "")),
            spicy=str(ai_payload.get("spicy", "")),
        )

    source_language = language_name(normalized_code)
    pack = starter_pack(normalized_code)
    if normalized_code != "en":
        return SpeakingHintsResponse(
            simple=pack["thanks"][0],
            conversational=f"{pack['want'][0]} {pack['thanks'][0]}",
            spicy=f"{pack['question'][0]}",
        )

    return SpeakingHintsResponse(
        simple="Yeah, that sounds good.",
        conversational=f"That sounds good, and I would like to try saying it in {source_language}.",
        spicy="That sounds good. What would you recommend next?",
    )


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
        "coucou": "привітик",
        "vale": "добре / окей",
        "allora": "ну / отже",
        "merhaba": "привіт",
    }
    return dictionary.get(term.lower(), f"{term} ({target_language})")
