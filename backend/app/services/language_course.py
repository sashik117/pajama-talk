from app.core.languages import language_name, normalize_language_code
from app.schemas.learning import LearningPathResponse, LearningPhrase, LearningStep


STARTER_PACKS: dict[str, dict[str, object]] = {
    "en": {
        "hello": ("Hi, I'm Sasha.", "hai aim Sasha", "Привіт, я Саша."),
        "want": ("I want a coffee, please.", "ai wont e kofi pliiz", "Я хочу каву, будь ласка."),
        "question": ("Can you help me?", "ken yu help mi", "Можеш мені допомогти?"),
        "thanks": ("Thanks, that sounds good.", "thenks, that saundz gud", "Дякую, звучить добре."),
    },
    "sk": {
        "hello": ("Ahoj, som Sasha.", "a-hoy som Sasha", "Привіт, я Саша."),
        "want": ("Prosím si kávu.", "pro-seem si kaa-vu", "Я хочу каву, будь ласка."),
        "question": ("Môžete mi pomôcť?", "mwo-zhe-te mi po-moots", "Можете мені допомогти?"),
        "thanks": ("Ďakujem, to znie dobre.", "dya-ku-yem to zni-ye dob-re", "Дякую, це звучить добре."),
    },
    "pl": {
        "hello": ("Cześć, jestem Sasha.", "cheshch yes-tem Sasha", "Привіт, я Саша."),
        "want": ("Poproszę kawę.", "po-pro-she ka-ve", "Попрошу каву."),
        "question": ("Możesz mi pomóc?", "mo-zhesh mi po-muts", "Можеш мені допомогти?"),
        "thanks": ("Dzięki, brzmi dobrze.", "jen-ki bzhmi dob-zhe", "Дякую, звучить добре."),
    },
    "cs": {
        "hello": ("Ahoj, jsem Sasha.", "a-hoy jsem Sasha", "Привіт, я Саша."),
        "want": ("Prosím kávu.", "pro-seem kaa-vu", "Каву, будь ласка."),
        "question": ("Můžete mi pomoct?", "moo-zhe-te mi po-motst", "Можете мені допомогти?"),
        "thanks": ("Díky, to zní dobře.", "dee-ki to znee dob-zhe", "Дякую, це звучить добре."),
    },
    "fr": {
        "hello": ("Salut, je suis Sasha.", "sa-lu zhe sui Sasha", "Привіт, я Саша."),
        "want": ("Je voudrais un café, s'il vous plaît.", "zhe voo-dre un ka-fe", "Я б хотіла каву, будь ласка."),
        "question": ("Vous pouvez m'aider ?", "vu pu-vey me-de", "Можете мені допомогти?"),
        "thanks": ("Merci, ça me va.", "mer-si sa me va", "Дякую, мені підходить."),
    },
    "es": {
        "hello": ("Hola, soy Sasha.", "o-la soy Sasha", "Привіт, я Саша."),
        "want": ("Quiero un café, por favor.", "kye-ro un ka-fe por fa-vor", "Я хочу каву, будь ласка."),
        "question": ("¿Puedes ayudarme?", "pwe-des a-yu-dar-me", "Можеш мені допомогти?"),
        "thanks": ("Gracias, suena bien.", "gra-syas swe-na byen", "Дякую, звучить добре."),
    },
    "it": {
        "hello": ("Ciao, sono Sasha.", "chao so-no Sasha", "Привіт, я Саша."),
        "want": ("Vorrei un caffè, per favore.", "vor-ray un kaf-fe", "Я б хотіла каву, будь ласка."),
        "question": ("Puoi aiutarmi?", "pwoi ai-u-tar-mi", "Можеш мені допомогти?"),
        "thanks": ("Grazie, mi va bene.", "gra-tsye mi va be-ne", "Дякую, мені підходить."),
    },
    "ko": {
        "hello": ("안녕하세요, 저는 Sasha예요.", "annyeonghaseyo, jeoneun Sasha-yeyo", "Вітаю, я Саша."),
        "want": ("커피 주세요.", "keopi juseyo", "Каву, будь ласка."),
        "question": ("도와줄 수 있어요?", "dowajul su isseoyo", "Можете допомогти?"),
        "thanks": ("고마워요, 좋아요.", "gomawoyo, joayo", "Дякую, добре."),
    },
    "ja": {
        "hello": ("こんにちは、Sashaです。", "konnichiwa, Sasha desu", "Добрий день, я Саша."),
        "want": ("コーヒーをください。", "koohii o kudasai", "Каву, будь ласка."),
        "question": ("手伝ってくれますか？", "tetsudatte kuremasu ka", "Можете допомогти?"),
        "thanks": ("ありがとう、いいですね。", "arigatou, ii desu ne", "Дякую, звучить добре."),
    },
    "zh": {
        "hello": ("你好，我是Sasha。", "ni hao, wo shi Sasha", "Привіт, я Саша."),
        "want": ("请给我一杯咖啡。", "qing gei wo yi bei kafei", "Дайте мені каву, будь ласка."),
        "question": ("你可以帮我吗？", "ni keyi bang wo ma", "Можеш мені допомогти?"),
        "thanks": ("谢谢，这很好。", "xiexie, zhe hen hao", "Дякую, це добре."),
    },
    "tr": {
        "hello": ("Merhaba, ben Sasha.", "mer-ha-ba ben Sasha", "Привіт, я Саша."),
        "want": ("Bir kahve istiyorum, lütfen.", "bir kah-ve is-ti-yo-rum lut-fen", "Я хочу каву, будь ласка."),
        "question": ("Bana yardım eder misin?", "ba-na yar-dym e-der mi-sin", "Можеш мені допомогти?"),
        "thanks": ("Teşekkürler, kulağa iyi geliyor.", "te-shek-kur-ler ku-laa iyi ge-li-yor", "Дякую, звучить добре."),
    },
}


def starter_pack(language_code: str) -> dict[str, tuple[str, str, str]]:
    code = normalize_language_code(language_code)
    return STARTER_PACKS.get(code, STARTER_PACKS["en"])  # type: ignore[return-value]


def starter_phrase(language_code: str, key: str) -> str:
    return starter_pack(language_code)[key][0]


def starter_meaning(language_code: str, key: str) -> str:
    return starter_pack(language_code)[key][2]


MEANING_TRANSLATIONS: dict[str, dict[str, str]] = {
    "uk": {
        "hello": "Привіт, я Sasha.",
        "want": "Я хочу каву, будь ласка.",
        "question": "Можеш мені допомогти?",
        "thanks": "Дякую, звучить добре.",
    },
    "en": {
        "hello": "Hi, I am Sasha.",
        "want": "I want a coffee, please.",
        "question": "Can you help me?",
        "thanks": "Thanks, that sounds good.",
    },
    "ru": {
        "hello": "Привет, я Sasha.",
        "want": "Я хочу кофе, пожалуйста.",
        "question": "Можешь мне помочь?",
        "thanks": "Спасибо, звучит хорошо.",
    },
    "pl": {
        "hello": "Cześć, jestem Sasha.",
        "want": "Poproszę kawę.",
        "question": "Możesz mi pomóc?",
        "thanks": "Dzięki, brzmi dobrze.",
    },
    "sk": {
        "hello": "Ahoj, som Sasha.",
        "want": "Prosím si kávu.",
        "question": "Môžeš mi pomôcť?",
        "thanks": "Ďakujem, znie to dobre.",
    },
    "cs": {
        "hello": "Ahoj, jsem Sasha.",
        "want": "Prosím kávu.",
        "question": "Můžeš mi pomoct?",
        "thanks": "Díky, zní to dobře.",
    },
    "fr": {
        "hello": "Salut, je suis Sasha.",
        "want": "Je voudrais un café, s'il vous plaît.",
        "question": "Vous pouvez m'aider ?",
        "thanks": "Merci, ça me va.",
    },
    "es": {
        "hello": "Hola, soy Sasha.",
        "want": "Quiero un café, por favor.",
        "question": "¿Puedes ayudarme?",
        "thanks": "Gracias, suena bien.",
    },
    "it": {
        "hello": "Ciao, sono Sasha.",
        "want": "Vorrei un caffè, per favore.",
        "question": "Puoi aiutarmi?",
        "thanks": "Grazie, mi va bene.",
    },
    "ko": {
        "hello": "안녕하세요, 저는 Sasha예요.",
        "want": "커피 주세요.",
        "question": "도와줄 수 있어요?",
        "thanks": "고마워요, 좋아요.",
    },
    "ja": {
        "hello": "こんにちは、Sashaです。",
        "want": "コーヒーをください。",
        "question": "手伝ってくれますか？",
        "thanks": "ありがとう、いいですね。",
    },
    "zh": {
        "hello": "你好，我是 Sasha。",
        "want": "请给我一杯咖啡。",
        "question": "你可以帮我吗？",
        "thanks": "谢谢，这很好。",
    },
    "tr": {
        "hello": "Merhaba, ben Sasha.",
        "want": "Bir kahve istiyorum, lütfen.",
        "question": "Bana yardım eder misin?",
        "thanks": "Teşekkürler, kulağa iyi geliyor.",
    },
}

COURSE_COPY: dict[str, dict[str, str]] = {
    "uk": {
        "assistant": "AI зараз працює як вчитель + співрозмовник для {name}: спочатку дає опору, потім просить сказати коротку живу фразу.",
        "next": "Спробуй у спікінгу сказати: {phrase}",
        "hello_title": "1. Представитись без паніки",
        "hello_goal": "Сказати хто ти і привітатись.",
        "hello_note": "Новачку не треба знати всю граматику. Спершу беремо готову фразу як конструктор.",
        "hello_task": "Повтори вголос: {phrase}",
        "want_title": "2. Попросити щось",
        "want_goal": "Вміти замовити або попросити базову річ.",
        "want_note": "Це перша корисна фраза для кафе, магазину і подорожей.",
        "want_task": "Заміни слово всередині фрази: {phrase}",
        "question_title": "3. Поставити питання",
        "question_goal": "Не зависати, коли треба попросити допомогу.",
        "question_note": "AI-співрозмовник буде провокувати такі питання у діалозі, щоб фраза стала автоматичною.",
        "question_task": "Скажи питання вголос: {phrase}",
    },
    "en": {
        "assistant": "AI now works as both teacher and conversation partner for {name}: first it gives support, then asks for one short real phrase.",
        "next": "Try saying this in Speaking: {phrase}",
        "hello_title": "1. Introduce yourself calmly",
        "hello_goal": "Say who you are and greet someone.",
        "hello_note": "A beginner does not need the whole grammar table first. We start with a ready phrase as a building block.",
        "hello_task": "Repeat out loud: {phrase}",
        "want_title": "2. Ask for something",
        "want_goal": "Order or ask for a basic thing.",
        "want_note": "This is a first useful phrase for cafes, shops and travel.",
        "want_task": "Swap one word inside the phrase: {phrase}",
        "question_title": "3. Ask a question",
        "question_goal": "Avoid freezing when you need help.",
        "question_note": "The AI partner will trigger these questions in dialogue until they feel automatic.",
        "question_task": "Say the question out loud: {phrase}",
    },
    "ru": {
        "assistant": "AI сейчас работает как учитель + собеседник для {name}: сначала дает опору, потом просит сказать короткую живую фразу.",
        "next": "Попробуй в спикинге сказать: {phrase}",
        "hello_title": "1. Представиться без паники",
        "hello_goal": "Сказать, кто ты, и поздороваться.",
        "hello_note": "Новичку не нужно сразу знать всю грамматику. Сначала берем готовую фразу как конструктор.",
        "hello_task": "Повтори вслух: {phrase}",
        "want_title": "2. Попросить что-то",
        "want_goal": "Уметь заказать или попросить базовую вещь.",
        "want_note": "Это первая полезная фраза для кафе, магазина и путешествий.",
        "want_task": "Замени одно слово внутри фразы: {phrase}",
        "question_title": "3. Задать вопрос",
        "question_goal": "Не зависать, когда нужно попросить помощь.",
        "question_note": "AI-собеседник будет провоцировать такие вопросы в диалоге, чтобы фраза стала автоматической.",
        "question_task": "Скажи вопрос вслух: {phrase}",
    },
}


def _copy_for(explanation_code: str) -> dict[str, str]:
    return COURSE_COPY.get(explanation_code, COURSE_COPY["en"])


def _meaning_for(key: str, explanation_code: str, fallback: str) -> str:
    return MEANING_TRANSLATIONS.get(explanation_code, MEANING_TRANSLATIONS["en"]).get(key, fallback)


def build_learning_path(language_code: str, explanation_code: str = "uk") -> LearningPathResponse:
    code = normalize_language_code(language_code)
    name = language_name(code)
    pack = starter_pack(code)
    copy = _copy_for(explanation_code)
    return LearningPathResponse(
        language_code=code,
        language_name=name,
        level="Starter A0-A1",
        assistant_role=copy["assistant"].format(name=name),
        next_room_prompt=copy["next"].format(phrase=pack["want"][0]),
        steps=[
            LearningStep(
                id=f"{code}-hello",
                title=copy["hello_title"],
                goal=copy["hello_goal"],
                teacher_note=copy["hello_note"],
                micro_task=copy["hello_task"].format(phrase=pack["hello"][0]),
                examples=[_phrase(pack["hello"], "hello", explanation_code)],
            ),
            LearningStep(
                id=f"{code}-want",
                title=copy["want_title"],
                goal=copy["want_goal"],
                teacher_note=copy["want_note"],
                micro_task=copy["want_task"].format(phrase=pack["want"][0]),
                examples=[_phrase(pack["want"], "want", explanation_code), _phrase(pack["thanks"], "thanks", explanation_code)],
            ),
            LearningStep(
                id=f"{code}-question",
                title=copy["question_title"],
                goal=copy["question_goal"],
                teacher_note=copy["question_note"],
                micro_task=copy["question_task"].format(phrase=pack["question"][0]),
                examples=[_phrase(pack["question"], "question", explanation_code)],
            ),
        ],
    )


def _phrase(raw: tuple[str, str, str], key: str, explanation_code: str) -> LearningPhrase:
    return LearningPhrase(phrase=raw[0], pronunciation=raw[1], meaning=_meaning_for(key, explanation_code, raw[2]))
