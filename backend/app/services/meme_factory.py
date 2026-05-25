from app.core.languages import normalize_language_code
from app.schemas.engagement import MemePuzzleResponse


def meme_puzzle(learning_words: list[str], language_code: str) -> MemePuzzleResponse:
    code = normalize_language_code(language_code)
    target = next((word for word in learning_words if _is_soft_enough(word)), _fallback_word(code))
    answer = _answer_for(code, target)
    pieces = _stable_shuffle(answer.split(" "))
    return MemePuzzleResponse(
        language_code=code,
        prompt="Build the meme sentence.",
        template="when the vocabulary finally leaves the textbook and joins real life",
        pieces=pieces,
        answer=answer,
        target_word=target,
    )


def _answer_for(code: str, target: str) -> str:
    templates = {
        "en": f"this {target} moment hits different",
        "uk": f"цей момент {target} реально зайшов",
        "ru": f"этот момент {target} реально зашел",
        "pl": f"ten moment {target} robi robotę",
        "sk": f"tento moment {target} fakt sadol",
        "cs": f"tenhle moment {target} fakt sedl",
        "fr": f"ce moment {target} passe crème",
        "es": f"este momento {target} me renta",
        "it": f"questo momento {target} ci sta",
        "de": f"dieser {target} moment läuft einfach",
        "pt": f"esse momento {target} bate diferente",
        "tr": f"bu {target} anı iyi geldi",
        "ja": f"この {target} の瞬間 刺さる",
        "ko": f"이 {target} 순간 느낌 있다",
        "zh": f"这个 {target} 时刻 很有感觉",
    }
    return templates.get(code, templates["en"])


def _fallback_word(code: str) -> str:
    return {
        "en": "cozy",
        "uk": "затишний",
        "ru": "уютный",
        "pl": "spoko",
        "sk": "pohoda",
        "cs": "pohoda",
        "fr": "coucou",
        "es": "vale",
        "it": "allora",
        "de": "hallo",
        "pt": "olá",
        "tr": "merhaba",
        "ja": "すごい",
        "ko": "안녕",
        "zh": "你好",
    }.get(code, "cozy")


def _is_soft_enough(word: str) -> bool:
    clean = word.strip().lower()
    blocked = {"shit", "fuck", "bitch", "asshole", "holy shit"}
    return bool(clean) and len(clean.split()) == 1 and not any(item in clean for item in blocked)


def _stable_shuffle(words: list[str]) -> list[str]:
    if len(words) <= 2:
        return words
    odd = words[1::2]
    even = words[0::2]
    return odd + even
