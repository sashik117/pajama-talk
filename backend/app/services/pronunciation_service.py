import re

from app.core.languages import normalize_native_language_code
from app.schemas.speaking import EchoResponse


def echo_feedback(phrase: str, transcript: str, target_language_code: str) -> EchoResponse:
    target_code = normalize_native_language_code(target_language_code)
    phrase_tokens = _tokens(phrase)
    transcript_tokens = _tokens(transcript)
    if not phrase_tokens or not transcript_tokens:
        return EchoResponse(
            score=0,
            feedback=_copy(target_code, "empty"),
            next_tip=_copy(target_code, "retry"),
            matched_text=transcript.strip(),
        )

    overlap = sum(1 for token in phrase_tokens if token in transcript_tokens)
    score = round(overlap / len(phrase_tokens) * 100)
    if score >= 86:
        key = "strong"
    elif score >= 55:
        key = "soft"
    else:
        key = "retry"
    return EchoResponse(
        score=score,
        feedback=_copy(target_code, key),
        next_tip=_stress_tip(phrase, target_code),
        matched_text=transcript.strip(),
    )


def _tokens(value: str) -> list[str]:
    return re.findall(r"[^\W\d_][^\W\d_'-]*", value.lower(), flags=re.UNICODE)


def _copy(code: str, key: str) -> str:
    copies = {
        "uk": {
            "empty": "Я не бачу розпізнаного тексту. Спробуй повторити ще раз повільніше.",
            "strong": "Текст супер. Звучить близько до цілі.",
            "soft": "Текст майже той самий. Додай трохи плавності й не рубай слова окремо.",
            "retry": "Поки що фраза зловилась не повністю. Послухай і повтори короткими шматками.",
        },
        "ru": {
            "empty": "Я не вижу распознанного текста. Попробуй повторить медленнее.",
            "strong": "Текст супер. Звучит близко к цели.",
            "soft": "Текст почти тот же. Добавь плавности и не руби слова отдельно.",
            "retry": "Пока фраза поймалась не полностью. Повтори короткими кусками.",
        },
        "en": {
            "empty": "I do not see recognized text yet. Try again a bit slower.",
            "strong": "Text is strong. Your shadowing is close to the target.",
            "soft": "Almost there. Make it smoother and connect the words more naturally.",
            "retry": "The phrase was only partly caught. Repeat it in smaller chunks.",
        },
    }
    return copies.get(code, copies["en"])[key]


def _stress_tip(phrase: str, code: str) -> str:
    target = phrase.split(" ")[-1].strip(".,!?") or phrase
    if code == "uk":
        return f"Ще раз: зроби останнє слово '{target}' трохи м'якшим і довшим."
    if code == "ru":
        return f"Еще раз: сделай последнее слово '{target}' чуть мягче и длиннее."
    return f"Try again with a softer, longer landing on '{target}'."
