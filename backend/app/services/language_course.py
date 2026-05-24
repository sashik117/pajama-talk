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


def build_learning_path(language_code: str) -> LearningPathResponse:
    code = normalize_language_code(language_code)
    name = language_name(code)
    pack = starter_pack(code)
    return LearningPathResponse(
        language_code=code,
        language_name=name,
        level="Starter A0-A1",
        assistant_role=(
            f"AI зараз працює як вчитель + співрозмовник для {name}: спочатку дає опору, "
            "потім просить сказати коротку живу фразу."
        ),
        next_room_prompt=f"Спробуй у спікінгу сказати: {pack['want'][0]}",
        steps=[
            LearningStep(
                id=f"{code}-hello",
                title="1. Представитись без паніки",
                goal="Сказати хто ти і привітатись.",
                teacher_note="Новачку не треба знати всю граматику. Спершу беремо готову фразу як конструктор.",
                micro_task=f"Повтори вголос: {pack['hello'][0]}",
                examples=[_phrase(pack["hello"])],
            ),
            LearningStep(
                id=f"{code}-want",
                title="2. Попросити щось",
                goal="Вміти замовити або попросити базову річ.",
                teacher_note="Це перша корисна фраза для кафе, магазину і подорожей.",
                micro_task=f"Заміни слово всередині фрази: {pack['want'][0]}",
                examples=[_phrase(pack["want"]), _phrase(pack["thanks"])],
            ),
            LearningStep(
                id=f"{code}-question",
                title="3. Поставити питання",
                goal="Не зависати, коли треба попросити допомогу.",
                teacher_note="AI-співрозмовник буде провокувати такі питання у діалозі, щоб фраза стала автоматичною.",
                micro_task=f"Скажи питання вголос: {pack['question'][0]}",
                examples=[_phrase(pack["question"])],
            ),
        ],
    )


def _phrase(raw: tuple[str, str, str]) -> LearningPhrase:
    return LearningPhrase(phrase=raw[0], pronunciation=raw[1], meaning=raw[2])
