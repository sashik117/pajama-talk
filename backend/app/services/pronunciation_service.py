import re
import unicodedata

from app.core.languages import language_name, normalize_language_code
from app.core.languages import normalize_native_language_code
from app.schemas.speaking import EchoResponse
from app.services.language_course import starter_pack


COMMON_PRONUNCIATIONS: dict[str, dict[str, str]] = {
    "en": {
        "cozy": "KOH-zee",
        "awkward": "AWK-werd",
        "deadline": "DED-line",
        "exam": "ig-ZAM",
        "coffee": "KAW-fee",
        "vibe": "vyb",
        "it hits different": "it hits DIF-er-ent",
    },
    "es": {
        "hola": "o-la",
        "vale": "BA-le",
        "gracias": "GRA-syas",
        "quiero": "KYE-ro",
        "cafe": "ka-FE",
        "por favor": "por fa-VOR",
        "puedes": "PWE-des",
        "ayudarme": "a-yu-DAR-me",
    },
    "pl": {
        "czesc": "cheshch",
        "spoko": "SPO-ko",
        "kawa": "KA-va",
        "poprosze": "po-PRO-she",
        "dzieki": "JEN-ki",
    },
    "sk": {
        "ahoj": "a-hoy",
        "prosim": "PRO-seem",
        "kava": "KAA-va",
        "dakujem": "DYA-ku-yem",
    },
    "cs": {
        "ahoj": "a-hoy",
        "prosim": "PRO-seem",
        "kava": "KAA-va",
        "diky": "DEE-ki",
    },
    "fr": {
        "salut": "sa-LU",
        "merci": "mer-SEE",
        "cafe": "ka-FE",
        "voudrais": "voo-DRE",
        "coucou": "koo-KOO",
    },
    "it": {
        "ciao": "CHAO",
        "grazie": "GRA-tsye",
        "caffe": "kaf-FE",
        "allora": "al-LO-ra",
    },
    "de": {
        "hallo": "HA-lo",
        "kaffee": "KAH-fe",
        "danke": "DAN-ke",
        "gemutlich": "ge-MOOT-likh",
    },
    "pt": {
        "ola": "o-LA",
        "obrigada": "o-bri-GA-da",
        "cafe": "ka-FE",
    },
    "tr": {
        "merhaba": "mer-ha-BA",
        "kahve": "KAH-ve",
        "lutfen": "LOOT-fen",
        "tesekkurler": "te-shek-KUR-ler",
    },
    "ja": {
        "こんにちは": "kon-ni-chi-wa",
        "すごい": "su-go-i",
        "ありがとう": "a-ri-ga-to",
        "コーヒー": "ko-hi",
    },
    "ko": {
        "안녕": "an-nyeong",
        "안녕하세요": "an-nyeong-ha-se-yo",
        "커피": "keo-pi",
        "고마워요": "go-ma-wo-yo",
    },
    "zh": {
        "你好": "ni hao",
        "谢谢": "xie xie",
        "咖啡": "ka fei",
        "很好": "hen hao",
    },
}


CYRILLIC_TO_LATIN: dict[str, str] = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "h",
    "ґ": "g",
    "д": "d",
    "е": "e",
    "є": "ye",
    "ё": "yo",
    "ж": "zh",
    "з": "z",
    "и": "y",
    "і": "i",
    "ї": "yi",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "kh",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "shch",
    "ь": "",
    "ы": "y",
    "э": "e",
    "ю": "yu",
    "я": "ya",
}


VOWELS = "aeiouy"


def pronunciation_hint(term: str, language_code: str = "en") -> str:
    clean_term = " ".join(term.strip().split())
    if not clean_term:
        return ""

    code = normalize_language_code(language_code)
    known = _known_pronunciations(code)
    key = _key(clean_term)
    if key in known:
        return known[key]

    words = re.findall(r"[^\W\d_][^\W\d_'-]*", clean_term, flags=re.UNICODE)
    if len(words) > 1:
        return " ".join(_word_pronunciation(word, code, known) for word in words)

    return _word_pronunciation(clean_term, code, known)


def usable_pronunciation(term: str, language_code: str, current: str | None = None) -> str:
    clean_current = (current or "").strip()
    if not clean_current or _looks_like_placeholder(term, clean_current):
        return pronunciation_hint(term, language_code)
    return clean_current


def _known_pronunciations(language_code: str) -> dict[str, str]:
    known = dict(COMMON_PRONUNCIATIONS.get(language_code, {}))
    for raw_phrase, raw_hint, _meaning in starter_pack(language_code).values():
        known[_key(raw_phrase)] = raw_hint
    return known


def _word_pronunciation(word: str, language_code: str, known: dict[str, str]) -> str:
    key = _key(word)
    if key in known:
        return known[key]
    if language_code in {"uk", "ru"}:
        return _hyphenate(_transliterate_cyrillic(word))
    if language_code in {"ja", "ko", "zh"}:
        return f"{language_name(language_code)} romanization: tap Listen"
    return _hyphenate(_latinize(word, language_code))


def _latinize(word: str, language_code: str) -> str:
    value = _strip_accents(word).casefold()
    if language_code == "es":
        value = re.sub(r"^h", "", value)
        value = value.replace("qu", "k").replace("ll", "y").replace("j", "h").replace("v", "b")
        value = re.sub(r"c([ei])", r"s\1", value)
    elif language_code == "fr":
        value = re.sub(r"(e|s|t)$", "", value)
        value = value.replace("ou", "u").replace("oi", "wa")
    elif language_code == "it":
        value = value.replace("ch", "k").replace("ci", "chi").replace("ce", "che")
    elif language_code == "de":
        value = value.replace("sch", "sh").replace("ch", "kh").replace("w", "v")
    elif language_code == "tr":
        value = value.replace("c", "j").replace("s", "s").replace("g", "g")
    return re.sub(r"[^a-z]+", "", value) or _strip_accents(word)


def _hyphenate(value: str) -> str:
    clean = re.sub(r"[^a-zA-Z]+", "", value)
    if not clean:
        return value.strip()
    chunks: list[str] = []
    current = ""
    for index, char in enumerate(clean):
        current += char
        next_char = clean[index + 1].lower() if index + 1 < len(clean) else ""
        if char.lower() in VOWELS and next_char and next_char not in VOWELS:
            chunks.append(current)
            current = ""
    if current:
        chunks.append(current)
    return "-".join(part for part in chunks if part)


def _transliterate_cyrillic(value: str) -> str:
    return "".join(CYRILLIC_TO_LATIN.get(char.casefold(), char) for char in value)


def _key(value: str) -> str:
    return re.sub(r"\s+", " ", _strip_accents(value).casefold()).strip(" /.,!?;:'\"()[]{}")


def _strip_accents(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _looks_like_placeholder(term: str, transcription: str) -> bool:
    current = transcription.strip().casefold()
    normalized_term = term.strip().casefold()
    return current in {
        normalized_term,
        f"/{normalized_term}/",
        f"[{normalized_term}]",
    }


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
