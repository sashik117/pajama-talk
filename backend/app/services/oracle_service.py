from datetime import date

from app.core.languages import normalize_language_code, normalize_native_language_code
from app.schemas.engagement import OracleIdiom, OracleResponse, SlangResponse


ORACLES = {
    "en": [
        (
            "Today you will catch a vibe. Do not let petty things ruin your day.",
            [("catch a vibe", "feel the mood"), ("petty things", "small annoying problems")],
        ),
        (
            "A tiny win will hit different if you actually notice it.",
            [("tiny win", "small success"), ("hit different", "feel special")],
        ),
    ],
    "uk": [
        ("Сьогодні маленька перемога зайде сильніше, ніж великий план.", [("зайде сильніше", "відчується краще"), ("маленька перемога", "невеликий успіх")]),
        ("Не тягни все на собі: одна спокійна фраза теж рахується.", [("тягнути на собі", "робити все самостійно"), ("теж рахується", "також має значення")]),
    ],
    "ru": [
        ("Сегодня маленькая победа зайдет сильнее, чем большой план.", [("зайдет сильнее", "почувствуется лучше"), ("маленькая победа", "небольшой успех")]),
        ("Не тащи все на себе: одна спокойная фраза тоже считается.", [("тащить на себе", "делать все самой"), ("тоже считается", "тоже имеет значение")]),
    ],
    "pl": [("Dzisiaj mały sukces zrobi robotę, jeśli go zauważysz.", [("zrobi robotę", "będzie skuteczny"), ("mały sukces", "small win")])],
    "sk": [("Dnes aj malý krok môže sadnúť presne tam, kde treba.", [("sadnúť", "fit well"), ("malý krok", "small step")])],
    "cs": [("Dnes i malý krok může sednout přesně, když ho nepřeskočíš.", [("sednout", "fit well"), ("malý krok", "small step")])],
    "fr": [("Aujourd'hui, une petite victoire peut faire toute la différence.", [("faire la différence", "matter a lot"), ("petite victoire", "small win")])],
    "es": [("Hoy una pequeña victoria puede sentirse brutal si la notas.", [("sentirse brutal", "feel great"), ("pequeña victoria", "small win")])],
    "it": [("Oggi una piccola vittoria può fare la differenza.", [("fare la differenza", "matter"), ("piccola vittoria", "small win")])],
    "de": [("Heute kann ein kleiner Erfolg den ganzen Tag drehen.", [("den Tag drehen", "change the day"), ("kleiner Erfolg", "small win")])],
    "pt": [("Hoje uma pequena vitória pode mudar o clima do dia.", [("mudar o clima", "shift the mood"), ("pequena vitória", "small win")])],
    "tr": [("Bugün küçük bir başarı bütün havanı değiştirebilir.", [("havanı değiştirmek", "change your mood"), ("küçük başarı", "small win")])],
    "ja": [("今日は小さな一歩が、思ったより効く日です。", [("小さな一歩", "small step"), ("効く", "work well / land")])],
    "ko": [("오늘은 작은 성공이 생각보다 크게 느껴질 거예요.", [("작은 성공", "small win"), ("크게 느껴지다", "feel meaningful")])],
    "zh": [("今天一个小小的进步，会比你想的更有分量。", [("小小的进步", "small progress"), ("有分量", "feel meaningful")])],
}

SLANG = {
    "en": ("it hits different", "something feels unusually good or meaningful", "This song hits different at night."),
    "uk": ("зайшло", "дуже сподобалось або добре відчулось", "Ця фраза мені прям зайшла."),
    "ru": ("зашло", "очень понравилось или хорошо почувствовалось", "Эта фраза мне прям зашла."),
    "pl": ("robi robotę", "works really well", "Ta fraza robi robotę."),
    "sk": ("to sadlo", "it landed well", "Tá fráza fakt sadla."),
    "cs": ("to sedlo", "it fit or landed well", "Ta věta fakt sedla."),
    "fr": ("ça passe crème", "it goes smoothly", "Cette phrase passe crème."),
    "es": ("me renta", "it is worth it / works for me", "Esa frase me renta."),
    "it": ("ci sta", "it works / sounds good", "Questa frase ci sta."),
    "de": ("läuft", "it works / all good", "Diese Phrase läuft."),
    "pt": ("bate diferente", "hits different", "Essa frase bate diferente."),
    "tr": ("iyi geldi", "it felt good", "Bu cümle iyi geldi."),
    "ja": ("刺さる", "it hits emotionally", "このフレーズ、刺さる。"),
    "ko": ("느낌 있다", "has a good vibe", "이 표현 느낌 있다."),
    "zh": ("有感觉", "has a vibe / feels right", "这个表达很有感觉。"),
}


def daily_oracle(user_id: int, language_code: str, target_language_code: str) -> OracleResponse:
    code = normalize_language_code(language_code)
    normalize_native_language_code(target_language_code)
    variants = ORACLES.get(code, ORACLES["en"])
    index = (date.today().toordinal() + user_id) % len(variants)
    prediction, idioms = variants[index]
    return OracleResponse(
        language_code=code,
        prediction=prediction,
        idioms=[OracleIdiom(phrase=phrase, explanation=explanation) for phrase, explanation in idioms],
    )


def slang_wheel(language_code: str) -> SlangResponse:
    code = normalize_language_code(language_code)
    term, meaning, example = SLANG.get(code, SLANG["en"])
    return SlangResponse(
        language_code=code,
        term=term,
        meaning=meaning,
        example=example,
        source_note="Trend-inspired daily slang. Live social fetch plugs into this service later.",
    )
