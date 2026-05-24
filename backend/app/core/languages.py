SUPPORTED_LANGUAGES = {
    "en": "English",
    "sk": "Slovak",
    "pl": "Polish",
    "cs": "Czech",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian",
    "ko": "Korean",
    "ja": "Japanese",
    "zh": "Chinese",
    "tr": "Turkish",
}


def normalize_language_code(value: str | None) -> str:
    code = (value or "en").strip().lower()
    return code if code in SUPPORTED_LANGUAGES else "en"


def language_name(code: str) -> str:
    return SUPPORTED_LANGUAGES.get(normalize_language_code(code), "English")
