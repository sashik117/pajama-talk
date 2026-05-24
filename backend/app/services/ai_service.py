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


COACH_COPY: dict[str, dict[str, str]] = {
    "uk": {
        "meme": "Коли '{term}' заходить у {source_language} sentence і все раптом звучить живіше.",
        "example_one": "{phrase} / слово для контексту: {term}",
        "example_two": "{phrase} / спробуй додати '{term}' у живу фразу.",
        "context_highlight": "Ймовірно важливе слово у цьому контексті. Додай його, якщо воно чіпляє.",
        "context_summary": "Це схоже на живий шматок {source_language}, не підручниковий приклад.",
        "context_hidden": "Тут важливі не лише слова, а тон: він звучить розмовно, трохи емоційно і дуже контекстно.",
        "learning_hook": " Спробуй використати '{term}' у відповіді, якщо підходить.",
        "roleplay_coffee": "{thanks} Тепер як teacher: спробуй відповісти фразою '{want}'.{hook}",
        "roleplay_airport": "{question} Добре для ситуації в аеропорту. Скажи коротко і я продовжу діалог.{hook}",
        "roleplay_interview": "{hello} Почни з представлення, потім додай одну просту фразу про себе.{hook}",
        "roleplay_default": "{question} Я як teacher підкину опору, а ти відповідай коротко.{hook}",
    },
    "ru": {
        "meme": "Когда '{term}' появляется в {source_language} sentence, фраза сразу звучит живее.",
        "example_one": "{phrase} / слово для контекста: {term}",
        "example_two": "{phrase} / попробуй добавить '{term}' в живую фразу.",
        "context_highlight": "Похоже на важное слово в этом контексте. Добавь его, если оно цепляет.",
        "context_summary": "Это похоже на живой кусок {source_language}, а не учебниковый пример.",
        "context_hidden": "Здесь важны не только слова, но и тон: он разговорный, немного эмоциональный и очень контекстный.",
        "learning_hook": " Попробуй использовать '{term}' в ответе, если подходит.",
        "roleplay_coffee": "{thanks} Теперь как teacher: попробуй ответить фразой '{want}'.{hook}",
        "roleplay_airport": "{question} Хорошо для ситуации в аэропорту. Скажи коротко, и я продолжу диалог.{hook}",
        "roleplay_interview": "{hello} Начни с представления, потом добавь одну простую фразу о себе.{hook}",
        "roleplay_default": "{question} Я как teacher дам опору, а ты отвечай коротко.{hook}",
    },
    "en": {
        "meme": "When '{term}' walks into a {source_language} sentence, it suddenly sounds more alive.",
        "example_one": "{phrase} / context word: {term}",
        "example_two": "{phrase} / try adding '{term}' to a real phrase.",
        "context_highlight": "Probably an important word in this context. Add it if it feels useful.",
        "context_summary": "This feels like a real piece of {source_language}, not a textbook example.",
        "context_hidden": "The tone matters here too: conversational, a bit emotional, and very context-dependent.",
        "learning_hook": " Try using '{term}' in your answer if it fits.",
        "roleplay_coffee": "{thanks} Now teacher mode: try replying with '{want}'.{hook}",
        "roleplay_airport": "{question} Good for an airport situation. Keep it short and I will continue the dialogue.{hook}",
        "roleplay_interview": "{hello} Start with an introduction, then add one simple sentence about yourself.{hook}",
        "roleplay_default": "{question} I will give you support as a teacher; answer with one short line.{hook}",
    },
}


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
    copy = _coach_copy(_target_code_from_language(target_language))
    return WordCreate(
        term=clean_term,
        language_code=normalized_code,
        translation=translation,
        transcription=f"/{clean_term.lower()}/",
        meme=copy["meme"].format(term=clean_term, source_language=source_language),
        example_one=copy["example_one"].format(phrase=pack["hello"][0], term=clean_term),
        example_two=copy["example_two"].format(phrase=pack["want"][0], term=clean_term),
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
    copy = _coach_copy(_target_code_from_language(target_language))
    words = [
        word.lower()
        for word in re.findall(r"[^\W\d_][^\W\d_'-]*", text, flags=re.UNICODE)
        if len(word.strip()) >= 2
    ]
    unique_words = list(dict.fromkeys(words))[:8]
    highlights = [
        ContextHighlight(
            phrase=word,
            explanation=copy["context_highlight"],
            addable_words=[word],
        )
        for word in unique_words[:3]
    ]
    return ContextAnalyzeResponse(
        summary=copy["context_summary"].format(source_language=source_language),
        hidden_meaning=copy["context_hidden"],
        highlights=highlights,
        suggested_words=unique_words,
    )


async def stream_roleplay_reply(
    room_id: str,
    user_text: str,
    tone: str,
    language_code: str = "en",
    learning_terms: list[str] | None = None,
    target_language_code: str = "uk",
) -> AsyncIterator[str]:
    reply = _roleplay_reply(room_id, user_text, tone, language_code, learning_terms or [], target_language_code)
    for word in reply.split(" "):
        await asyncio.sleep(0.03)
        yield word + " "


def _roleplay_reply(
    room_id: str,
    user_text: str,
    tone: str,
    language_code: str,
    learning_terms: list[str],
    target_language_code: str,
) -> str:
    pack = starter_pack(language_code)
    copy = _coach_copy(target_language_code)
    learning_hook = ""
    if learning_terms:
        term = learning_terms[0]
        learning_hook = copy["learning_hook"].format(term=term)

    if language_code != "en":
        if "coffee" in room_id:
            return copy["roleplay_coffee"].format(thanks=pack["thanks"][0], want=pack["want"][0], hook=learning_hook)
        if "airport" in room_id:
            return copy["roleplay_airport"].format(question=pack["question"][0], hook=learning_hook)
        if "interview" in room_id:
            return copy["roleplay_interview"].format(hello=pack["hello"][0], hook=learning_hook)
        return copy["roleplay_default"].format(question=pack["question"][0], hook=learning_hook)

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


def _coach_copy(target_language_code: str) -> dict[str, str]:
    return COACH_COPY.get(target_language_code, COACH_COPY["en"])


def _target_code_from_language(target_language: str) -> str:
    value = target_language.strip().lower()
    if value in {"uk", "ukrainian"} or "укра" in value:
        return "uk"
    if value in {"ru", "russian"} or "рус" in value:
        return "ru"
    return "en"


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
