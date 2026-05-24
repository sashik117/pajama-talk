SUPPORTED_LEARNING_LANGUAGES = {
    "en": "English",
    "uk": "Ukrainian",
    "ru": "Russian",
    "sk": "Slovak",
    "pl": "Polish",
    "cs": "Czech",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian",
    "de": "German",
    "pt": "Portuguese",
    "ko": "Korean",
    "ja": "Japanese",
    "zh": "Chinese",
    "tr": "Turkish",
}

SUPPORTED_NATIVE_LANGUAGES = {
    **SUPPORTED_LEARNING_LANGUAGES,
    "uk": "Ukrainian",
    "ru": "Russian",
}

SUPPORTED_LANGUAGES = SUPPORTED_LEARNING_LANGUAGES


def normalize_language_code(value: str | None) -> str:
    code = (value or "en").strip().lower()
    return code if code in SUPPORTED_LEARNING_LANGUAGES else "en"


def normalize_native_language_code(value: str | None) -> str:
    code = (value or "uk").strip().lower()
    return code if code in SUPPORTED_NATIVE_LANGUAGES else "uk"


def language_name(code: str) -> str:
    return SUPPORTED_NATIVE_LANGUAGES.get(code, SUPPORTED_LEARNING_LANGUAGES.get(normalize_language_code(code), "English"))
