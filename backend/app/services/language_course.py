from app.core.languages import language_name, normalize_language_code
from app.schemas.learning import (
    LearningDailyTask,
    LearningPathResponse,
    LearningPhrase,
    LearningPracticeItem,
    LearningStep,
    LearningVocabularyItem,
)


STARTER_PACKS: dict[str, dict[str, object]] = {
    "en": {
        "hello": ("Hi, I'm Sasha.", "hai aim Sasha", "Привіт, я Саша."),
        "want": ("I want a coffee, please.", "ai wont e kofi pliiz", "Я хочу каву, будь ласка."),
        "question": ("Can you help me?", "ken yu help mi", "Можеш мені допомогти?"),
        "thanks": ("Thanks, that sounds good.", "thenks, that saundz gud", "Дякую, звучить добре."),
    },
    "uk": {
        "hello": ("Привіт, я Саша.", "pry-vit ya Sa-sha", "Привіт, я Саша."),
        "want": ("Я хочу каву, будь ласка.", "ya kho-chu ka-vu bud las-ka", "Я хочу каву, будь ласка."),
        "question": ("Можеш мені допомогти?", "mo-zhesh me-ni do-po-moh-ty", "Можеш мені допомогти?"),
        "thanks": ("Дякую, звучить добре.", "dya-ku-yu zvu-chyt dob-re", "Дякую, звучить добре."),
    },
    "ru": {
        "hello": ("Привет, я Саша.", "pri-vet ya Sa-sha", "Привіт, я Саша."),
        "want": ("Я хочу кофе, пожалуйста.", "ya ha-chu ko-fe pa-zha-luy-sta", "Я хочу каву, будь ласка."),
        "question": ("Можешь мне помочь?", "mo-zhesh mnye po-moch", "Можеш мені допомогти?"),
        "thanks": ("Спасибо, звучит хорошо.", "spa-si-bo zvu-chit ha-ra-sho", "Дякую, звучить добре."),
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
    "de": {
        "hello": ("Hallo, ich bin Sasha.", "ha-lo ikh bin Sasha", "Привіт, я Саша."),
        "want": ("Ich hätte gern einen Kaffee.", "ikh het-te gern ai-nen ka-fe", "Я б хотіла каву."),
        "question": ("Kannst du mir helfen?", "kanst du mir hel-fen", "Можеш мені допомогти?"),
        "thanks": ("Danke, das klingt gut.", "dan-ke das klingt gut", "Дякую, звучить добре."),
    },
    "pt": {
        "hello": ("Olá, eu sou Sasha.", "o-la eu sou Sasha", "Привіт, я Саша."),
        "want": ("Queria um café, por favor.", "ke-ri-a um ka-fe por fa-vor", "Я б хотіла каву, будь ласка."),
        "question": ("Pode me ajudar?", "po-de me a-ju-dar", "Можете мені допомогти?"),
        "thanks": ("Obrigada, parece bom.", "o-bri-ga-da pa-re-se bom", "Дякую, звучить добре."),
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


VOCAB_BANK: dict[str, dict[str, tuple[str, str]]] = {
    "en": {
        "hello": ("Hi", "hai"),
        "coffee": ("coffee", "ko-fee"),
        "help": ("help", "help"),
        "thanks": ("Thanks", "thenks"),
    },
    "uk": {
        "hello": ("Привіт", "pry-vit"),
        "coffee": ("кава", "ka-va"),
        "help": ("допомогти", "do-po-moh-ty"),
        "thanks": ("Дякую", "dya-ku-yu"),
    },
    "ru": {
        "hello": ("Привет", "pri-vet"),
        "coffee": ("кофе", "ko-fe"),
        "help": ("помочь", "po-moch"),
        "thanks": ("Спасибо", "spa-si-bo"),
    },
    "sk": {
        "hello": ("Ahoj", "a-hoy"),
        "coffee": ("káva", "kaa-va"),
        "help": ("pomôcť", "po-moots"),
        "thanks": ("Ďakujem", "dya-ku-yem"),
    },
    "pl": {
        "hello": ("Cześć", "cheshch"),
        "coffee": ("kawa", "ka-va"),
        "help": ("pomóc", "po-muts"),
        "thanks": ("Dzięki", "jen-ki"),
    },
    "cs": {
        "hello": ("Ahoj", "a-hoy"),
        "coffee": ("káva", "kaa-va"),
        "help": ("pomoct", "po-motst"),
        "thanks": ("Díky", "dee-ki"),
    },
    "fr": {
        "hello": ("Salut", "sa-lu"),
        "coffee": ("café", "ka-fe"),
        "help": ("aider", "e-de"),
        "thanks": ("Merci", "mer-si"),
    },
    "es": {
        "hello": ("Hola", "o-la"),
        "coffee": ("café", "ka-fe"),
        "help": ("ayudar", "a-yu-dar"),
        "thanks": ("Gracias", "gra-syas"),
    },
    "it": {
        "hello": ("Ciao", "chao"),
        "coffee": ("caffè", "kaf-fe"),
        "help": ("aiutare", "ai-u-ta-re"),
        "thanks": ("Grazie", "gra-tsye"),
    },
    "de": {
        "hello": ("Hallo", "ha-lo"),
        "coffee": ("Kaffee", "ka-fe"),
        "help": ("helfen", "hel-fen"),
        "thanks": ("Danke", "dan-ke"),
    },
    "pt": {
        "hello": ("Olá", "o-la"),
        "coffee": ("café", "ka-fe"),
        "help": ("ajudar", "a-ju-dar"),
        "thanks": ("Obrigada", "o-bri-ga-da"),
    },
    "ko": {
        "hello": ("안녕하세요", "annyeonghaseyo"),
        "coffee": ("커피", "keopi"),
        "help": ("도와주세요", "dowajuseyo"),
        "thanks": ("고마워요", "gomawoyo"),
    },
    "ja": {
        "hello": ("こんにちは", "konnichiwa"),
        "coffee": ("コーヒー", "koohii"),
        "help": ("手伝って", "tetsudatte"),
        "thanks": ("ありがとう", "arigatou"),
    },
    "zh": {
        "hello": ("你好", "ni hao"),
        "coffee": ("咖啡", "ka fei"),
        "help": ("帮忙", "bang mang"),
        "thanks": ("谢谢", "xie xie"),
    },
    "tr": {
        "hello": ("Merhaba", "mer-ha-ba"),
        "coffee": ("kahve", "kah-ve"),
        "help": ("yardım", "yar-dym"),
        "thanks": ("Teşekkürler", "te-shek-kur-ler"),
    },
}


VOCAB_MEANINGS: dict[str, dict[str, str]] = {
    "uk": {
        "hello": "привітання",
        "coffee": "кава",
        "help": "допомога",
        "thanks": "дякую",
    },
    "ru": {
        "hello": "приветствие",
        "coffee": "кофе",
        "help": "помощь",
        "thanks": "спасибо",
    },
    "en": {
        "hello": "greeting",
        "coffee": "coffee",
        "help": "help",
        "thanks": "thanks",
    },
    "pl": {
        "hello": "powitanie",
        "coffee": "kawa",
        "help": "pomoc",
        "thanks": "dziękuję",
    },
    "sk": {
        "hello": "pozdrav",
        "coffee": "káva",
        "help": "pomoc",
        "thanks": "ďakujem",
    },
    "cs": {
        "hello": "pozdrav",
        "coffee": "káva",
        "help": "pomoc",
        "thanks": "děkuji",
    },
    "fr": {
        "hello": "salutation",
        "coffee": "café",
        "help": "aide",
        "thanks": "merci",
    },
    "es": {
        "hello": "saludo",
        "coffee": "café",
        "help": "ayuda",
        "thanks": "gracias",
    },
    "it": {
        "hello": "saluto",
        "coffee": "caffè",
        "help": "aiuto",
        "thanks": "grazie",
    },
    "de": {
        "hello": "Begrüßung",
        "coffee": "Kaffee",
        "help": "Hilfe",
        "thanks": "Danke",
    },
    "pt": {
        "hello": "saudação",
        "coffee": "café",
        "help": "ajuda",
        "thanks": "obrigada",
    },
    "tr": {
        "hello": "selamlaşma",
        "coffee": "kahve",
        "help": "yardım",
        "thanks": "teşekkür",
    },
    "ja": {
        "hello": "あいさつ",
        "coffee": "コーヒー",
        "help": "助け",
        "thanks": "ありがとう",
    },
    "ko": {
        "hello": "인사",
        "coffee": "커피",
        "help": "도움",
        "thanks": "고마워요",
    },
    "zh": {
        "hello": "问候",
        "coffee": "咖啡",
        "help": "帮助",
        "thanks": "谢谢",
    },
}


STEP_VOCAB_CONCEPTS = {
    "hello": ["hello"],
    "want": ["coffee"],
    "question": ["help"],
    "thanks": ["thanks"],
}


def _vocabulary_item(language_code: str, concept: str, explanation_code: str) -> LearningVocabularyItem:
    term, pronunciation = VOCAB_BANK.get(language_code, VOCAB_BANK["en"]).get(concept, VOCAB_BANK["en"][concept])
    meaning = VOCAB_MEANINGS.get(explanation_code, VOCAB_MEANINGS["en"]).get(concept, concept)
    return LearningVocabularyItem(term=term, pronunciation=pronunciation, meaning=meaning)


PRACTICE_COPY: dict[str, dict[str, str]] = {
    "uk": {
        "vocab_prompt": "Що означає “{term}”?",
        "phrase_prompt": "Яка фраза підходить для: {goal}",
        "vocab_feedback": "Так. Спершу прив'язуємо звук до значення, потім переносимо слово у фразу.",
        "phrase_feedback": "Так. Це готова репліка для спікінгу, не сухе правило.",
    },
    "ru": {
        "vocab_prompt": "Что означает “{term}”?",
        "phrase_prompt": "Какая фраза подходит для: {goal}",
        "vocab_feedback": "Да. Сначала связываем звук со значением, потом переносим слово во фразу.",
        "phrase_feedback": "Да. Это готовая реплика для спикинга, не сухое правило.",
    },
    "en": {
        "vocab_prompt": "What does “{term}” mean?",
        "phrase_prompt": "Which phrase fits: {goal}",
        "vocab_feedback": "Yes. First connect the sound to the meaning, then use it in a phrase.",
        "phrase_feedback": "Yes. This is a ready speaking turn, not a dry rule.",
    },
    "pl": {
        "vocab_prompt": "Co znaczy “{term}”?",
        "phrase_prompt": "Która fraza pasuje do: {goal}",
        "vocab_feedback": "Tak. Najpierw łączymy dźwięk ze znaczeniem, potem używamy go w zdaniu.",
        "phrase_feedback": "Tak. To gotowa wypowiedź do mówienia, nie sucha reguła.",
    },
    "sk": {
        "vocab_prompt": "Čo znamená “{term}”?",
        "phrase_prompt": "Ktorá fráza sa hodí na: {goal}",
        "vocab_feedback": "Áno. Najprv spojíme zvuk s významom, potom slovo použijeme vo fráze.",
        "phrase_feedback": "Áno. Toto je hotová replika na hovorenie, nie suché pravidlo.",
    },
    "cs": {
        "vocab_prompt": "Co znamená “{term}”?",
        "phrase_prompt": "Která fráze se hodí pro: {goal}",
        "vocab_feedback": "Ano. Nejdřív spojíme zvuk s významem, potom slovo použijeme ve frázi.",
        "phrase_feedback": "Ano. Je to hotová replika pro mluvení, ne suché pravidlo.",
    },
    "fr": {
        "vocab_prompt": "Que signifie “{term}” ?",
        "phrase_prompt": "Quelle phrase convient pour : {goal}",
        "vocab_feedback": "Oui. On relie d'abord le son au sens, puis on l'utilise dans une phrase.",
        "phrase_feedback": "Oui. C'est une réplique prête pour l'oral, pas une règle sèche.",
    },
    "es": {
        "vocab_prompt": "¿Qué significa “{term}”?",
        "phrase_prompt": "Qué frase encaja con: {goal}",
        "vocab_feedback": "Sí. Primero conectamos el sonido con el significado y luego lo usamos en una frase.",
        "phrase_feedback": "Sí. Es una respuesta lista para hablar, no una regla seca.",
    },
    "it": {
        "vocab_prompt": "Cosa significa “{term}”?",
        "phrase_prompt": "Quale frase va bene per: {goal}",
        "vocab_feedback": "Sì. Prima colleghiamo il suono al significato, poi lo usiamo in una frase.",
        "phrase_feedback": "Sì. È una risposta pronta per parlare, non una regola asciutta.",
    },
    "de": {
        "vocab_prompt": "Was bedeutet “{term}”?",
        "phrase_prompt": "Welche Phrase passt zu: {goal}",
        "vocab_feedback": "Ja. Erst verbinden wir Klang und Bedeutung, dann nutzen wir das Wort in einer Phrase.",
        "phrase_feedback": "Ja. Das ist ein fertiger Sprechzug, keine trockene Regel.",
    },
    "pt": {
        "vocab_prompt": "O que significa “{term}”?",
        "phrase_prompt": "Qual frase combina com: {goal}",
        "vocab_feedback": "Sim. Primeiro ligamos o som ao significado, depois usamos numa frase.",
        "phrase_feedback": "Sim. É uma fala pronta para praticar, não uma regra seca.",
    },
    "tr": {
        "vocab_prompt": "“{term}” ne demek?",
        "phrase_prompt": "Hangi ifade şuna uyar: {goal}",
        "vocab_feedback": "Evet. Önce sesi anlamla bağlıyoruz, sonra kelimeyi cümlede kullanıyoruz.",
        "phrase_feedback": "Evet. Bu konuşma için hazır bir cevap, kuru bir kural değil.",
    },
    "ja": {
        "vocab_prompt": "“{term}” はどういう意味？",
        "phrase_prompt": "どのフレーズが合う？ {goal}",
        "vocab_feedback": "OK。まず音と意味をつなげて、それからフレーズで使います。",
        "phrase_feedback": "OK。これは会話でそのまま使える返事です。",
    },
    "ko": {
        "vocab_prompt": "“{term}”은 무슨 뜻이에요?",
        "phrase_prompt": "어떤 문장이 맞아요: {goal}",
        "vocab_feedback": "좋아요. 먼저 소리와 뜻을 연결하고, 그다음 문장에서 써요.",
        "phrase_feedback": "좋아요. 이건 말하기에 바로 쓰는 대답이에요.",
    },
    "zh": {
        "vocab_prompt": "“{term}”是什么意思？",
        "phrase_prompt": "哪个句子适合：{goal}",
        "vocab_feedback": "对。先把声音和意思连起来，再放进句子里用。",
        "phrase_feedback": "对。这是可以直接开口说的回答，不是干规则。",
    },
}


def _practice_copy(explanation_code: str) -> dict[str, str]:
    return PRACTICE_COPY.get(explanation_code, PRACTICE_COPY["en"])


def _ordered_options(correct: str, candidates: list[str], limit: int = 3) -> list[str]:
    options = [correct]
    for candidate in candidates:
        if candidate != correct and candidate not in options:
            options.append(candidate)
        if len(options) == limit:
            break
    return options


def _practice_items(
    language_code: str,
    key: str,
    pack: dict[str, tuple[str, str, str]],
    explanation_code: str,
    goal: str,
) -> list[LearningPracticeItem]:
    copy = _practice_copy(explanation_code)
    concept = STEP_VOCAB_CONCEPTS.get(key, ["hello"])[0]
    vocab = _vocabulary_item(language_code, concept, explanation_code)
    meanings = VOCAB_MEANINGS.get(explanation_code, VOCAB_MEANINGS["en"])
    meaning_options = _ordered_options(vocab.meaning, [meanings[item] for item in ("hello", "coffee", "help", "thanks")])
    phrase_options = _ordered_options(pack[key][0], [pack[item][0] for item in ("hello", "want", "question", "thanks")])
    return [
        LearningPracticeItem(
            id=f"{language_code}-{key}-meaning",
            prompt=copy["vocab_prompt"].format(term=vocab.term),
            options=meaning_options,
            correct_answer=vocab.meaning,
            feedback=copy["vocab_feedback"],
        ),
        LearningPracticeItem(
            id=f"{language_code}-{key}-phrase",
            prompt=copy["phrase_prompt"].format(goal=goal),
            options=phrase_options,
            correct_answer=pack[key][0],
            feedback=copy["phrase_feedback"],
        ),
    ]


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
    "de": {
        "hello": "Hallo, ich bin Sasha.",
        "want": "Ich hätte gern einen Kaffee.",
        "question": "Kannst du mir helfen?",
        "thanks": "Danke, das klingt gut.",
    },
    "pt": {
        "hello": "Olá, eu sou Sasha.",
        "want": "Queria um café, por favor.",
        "question": "Pode me ajudar?",
        "thanks": "Obrigada, parece bom.",
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


def _profile_step_keys(current_level: str) -> list[str]:
    level = (current_level or "Starter").strip().lower()
    if level in {"starter", "a0", "a1"}:
        return ["hello", "want", "question"]
    if level == "a2":
        return ["want", "question", "thanks"]
    return ["question", "thanks", "want"]


def _effort_hint(effort_level: str) -> str:
    effort = (effort_level or "Steady").strip()
    hints = {
        "Light": "1 tiny answer",
        "Steady": "2 spoken turns",
        "Intense": "3-turn mini dialogue",
    }
    return hints.get(effort, hints["Steady"])


def _effort_minutes(effort_level: str) -> tuple[int, int, int]:
    effort = (effort_level or "Steady").strip()
    if effort == "Light":
        return (2, 2, 1)
    if effort == "Intense":
        return (5, 4, 4)
    return (3, 3, 2)


def _level_band(current_level: str) -> str:
    level = (current_level or "Starter").strip().lower()
    if level in {"starter", "a0", "a1"}:
        return "starter"
    if level == "a2":
        return "builder"
    return "speaker"


LEARNING_COPY: dict[str, dict[str, str]] = {
    "uk": {
        "profile": "{current} -> {target} · {effort}. План підлаштований під твій рівень, мову та темп.",
        "coach_starter": "Починаємо з готових фраз. Тобі не треба знати всю граматику: спершу слухаєш, повторюєш і міняєш одне слово.",
        "coach_builder": "Тут головне не застрягати. Беремо коротку фразу, додаємо питання і одразу переносимо це у спікінг.",
        "coach_speaker": "Ти вже тренуєш не окремі слова, а живі репліки: питання, уточнення, реакцію і маленьку історію.",
        "review": "Слова зі статусом learning мають повертатися у спікінгу та повторенні, поки не стануть автоматичними.",
        "drill": "У спікінгу AI має витягнути з тебе цю фразу: {phrase}",
        "listen_title": "Почути фразу",
        "listen_detail": "Послухай вимову і прочитай підказку “як читати”.",
        "shadow_title": "Повторити вголос",
        "shadow_detail": "Введи або скажи фразу після прослуховування. Не ідеально - нормально.",
        "speak_title": "Сказати в діалозі",
        "speak_detail": "Зайди у кімнату і використай фразу в реальній репліці.",
        "review_title": "Закріпити слово",
        "review_detail": "Додай ключову фразу в словник або повтори те, що вже чекає.",
        "objective_hello": "привітатися і представитися",
        "objective_want": "попросити базову річ без паніки",
        "objective_question": "поставити коротке питання",
        "objective_thanks": "відреагувати і завершити репліку",
    },
    "ru": {
        "profile": "{current} -> {target} · {effort}. План подстроен под твой уровень, язык и темп.",
        "coach_starter": "Начинаем с готовых фраз. Не нужно знать всю грамматику: сначала слушаешь, повторяешь и меняешь одно слово.",
        "coach_builder": "Главное не зависать. Берем короткую фразу, добавляем вопрос и сразу переносим это в спикинг.",
        "coach_speaker": "Ты тренируешь уже не отдельные слова, а живые реплики: вопрос, уточнение, реакцию и маленькую историю.",
        "review": "Слова со статусом learning должны возвращаться в спикинге и повторении, пока не станут автоматическими.",
        "drill": "В спикинге AI должен вытянуть из тебя эту фразу: {phrase}",
        "listen_title": "Услышать фразу",
        "listen_detail": "Послушай произношение и прочитай подсказку “как читать”.",
        "shadow_title": "Повторить вслух",
        "shadow_detail": "Введи или скажи фразу после прослушивания. Не идеально - нормально.",
        "speak_title": "Сказать в диалоге",
        "speak_detail": "Зайди в комнату и используй фразу в настоящей реплике.",
        "review_title": "Закрепить слово",
        "review_detail": "Добавь ключевую фразу в словарь или повтори то, что уже ждет.",
        "objective_hello": "поздороваться и представиться",
        "objective_want": "попросить базовую вещь без паники",
        "objective_question": "задать короткий вопрос",
        "objective_thanks": "отреагировать и завершить реплику",
    },
    "en": {
        "profile": "{current} -> {target} · {effort}. The plan follows your level, language and daily effort.",
        "coach_starter": "Start with ready phrases. You do not need the whole grammar table first: listen, repeat, then swap one word.",
        "coach_builder": "The goal is not to freeze. Take a short phrase, add a question, then move it into Speaking.",
        "coach_speaker": "You are training live turns now: question, clarification, reaction and a tiny story.",
        "review": "Words marked learning should return in Speaking and SRS until they feel automatic.",
        "drill": "In Speaking, AI should pull this phrase from you: {phrase}",
        "listen_title": "Hear the phrase",
        "listen_detail": "Listen to pronunciation and read the how-to-say hint.",
        "shadow_title": "Repeat out loud",
        "shadow_detail": "Type or say the phrase after listening. Imperfect is fine.",
        "speak_title": "Use it in dialogue",
        "speak_detail": "Enter a room and use the phrase in a real reply.",
        "review_title": "Lock one word in",
        "review_detail": "Add the key phrase to Dictionary or review the next due item.",
        "objective_hello": "greet and introduce yourself",
        "objective_want": "ask for a basic thing calmly",
        "objective_question": "ask a short question",
        "objective_thanks": "react and close the turn",
    },
}


def _learning_copy(explanation_code: str) -> dict[str, str]:
    return LEARNING_COPY.get(explanation_code, LEARNING_COPY["en"])


def _coach_tip(explanation_code: str, current_level: str) -> str:
    copy = _learning_copy(explanation_code)
    band = _level_band(current_level)
    return copy[f"coach_{band}"]


def _daily_plan(
    explanation_code: str,
    effort_level: str,
    first_phrase: str,
    review_phrase: str,
) -> list[LearningDailyTask]:
    copy = _learning_copy(explanation_code)
    listen_minutes, speak_minutes, review_minutes = _effort_minutes(effort_level)
    return [
        LearningDailyTask(
            id="listen",
            title=copy["listen_title"],
            detail=copy["listen_detail"],
            action="shadow",
            phrase=first_phrase,
            minutes=listen_minutes,
        ),
        LearningDailyTask(
            id="speak",
            title=copy["speak_title"],
            detail=copy["speak_detail"],
            action="speak",
            phrase=first_phrase,
            minutes=speak_minutes,
        ),
        LearningDailyTask(
            id="review",
            title=copy["review_title"],
            detail=copy["review_detail"],
            action="review",
            phrase=review_phrase,
            minutes=review_minutes,
        ),
    ]


def _objectives(step_keys: list[str], explanation_code: str) -> list[str]:
    copy = _learning_copy(explanation_code)
    return [copy[f"objective_{key}"] for key in step_keys if f"objective_{key}" in copy]


def build_learning_path(
    language_code: str,
    explanation_code: str = "uk",
    current_level: str = "Starter",
    target_level: str = "A1",
    effort_level: str = "Steady",
) -> LearningPathResponse:
    code = normalize_language_code(language_code)
    name = language_name(code)
    pack = starter_pack(code)
    copy = _copy_for(explanation_code)
    learning_copy = _learning_copy(explanation_code)
    step_keys = _profile_step_keys(current_level)
    titles = {
        "hello": copy["hello_title"],
        "want": copy["want_title"],
        "question": copy["question_title"],
        "thanks": {
            "uk": "4. Відреагувати природно",
            "ru": "4. Отреагировать естественно",
            "en": "4. React naturally",
        }.get(explanation_code, "4. React naturally"),
    }
    goals = {
        "hello": copy["hello_goal"],
        "want": copy["want_goal"],
        "question": copy["question_goal"],
        "thanks": {
            "uk": "Не мовчати після відповіді співрозмовника.",
            "ru": "Не молчать после ответа собеседника.",
            "en": "Avoid going silent after the other person answers.",
        }.get(explanation_code, "Avoid going silent after the other person answers."),
    }
    notes = {
        "hello": copy["hello_note"],
        "want": copy["want_note"],
        "question": copy["question_note"],
        "thanks": {
            "uk": "Реакції роблять діалог живим: подякуй, погодься або попроси продовжити.",
            "ru": "Реакции делают диалог живым: поблагодари, согласись или попроси продолжить.",
            "en": "Reactions make dialogue alive: thank them, agree, or invite them to continue.",
        }.get(explanation_code, "Reactions make dialogue alive: thank them, agree, or invite them to continue."),
    }
    tasks = {
        "hello": copy["hello_task"],
        "want": copy["want_task"],
        "question": copy["question_task"],
        "thanks": {
            "uk": "Відповідай після репліки AI: {phrase}",
            "ru": "Ответь после реплики AI: {phrase}",
            "en": "Reply after the AI turn: {phrase}",
        }.get(explanation_code, "Reply after the AI turn: {phrase}"),
    }
    examples = {
        "hello": [_phrase(pack["hello"], "hello", explanation_code)],
        "want": [_phrase(pack["want"], "want", explanation_code), _phrase(pack["thanks"], "thanks", explanation_code)],
        "question": [_phrase(pack["question"], "question", explanation_code)],
        "thanks": [_phrase(pack["thanks"], "thanks", explanation_code)],
    }
    first_phrase = pack[step_keys[0]][0]
    review_phrase = pack["thanks"][0]
    return LearningPathResponse(
        language_code=code,
        language_name=name,
        level=f"{current_level or 'Starter'} -> {target_level or 'A1'} · {_effort_hint(effort_level)}",
        assistant_role=copy["assistant"].format(name=name),
        next_room_prompt=copy["next"].format(phrase=pack["want"][0]),
        profile_summary=learning_copy["profile"].format(
            current=current_level or "Starter",
            target=target_level or "A1",
            effort=_effort_hint(effort_level),
        ),
        coach_tip=_coach_tip(explanation_code, current_level),
        review_prompt=learning_copy["review"],
        speaking_drill=learning_copy["drill"].format(phrase=first_phrase),
        objectives=_objectives(step_keys, explanation_code),
        daily_plan=_daily_plan(explanation_code, effort_level, first_phrase, review_phrase),
        steps=[
            LearningStep(
                id=f"{code}-{key}",
                title=titles[key],
                goal=goals[key],
                teacher_note=notes[key],
                micro_task=f"{tasks[key].format(phrase=pack[key][0])} · {_effort_hint(effort_level)}",
                examples=examples[key],
                vocabulary=[
                    _vocabulary_item(code, concept, explanation_code)
                    for concept in STEP_VOCAB_CONCEPTS.get(key, [])
                ],
                practice=_practice_items(code, key, pack, explanation_code, goals[key]),
            )
            for key in step_keys
        ],
    )


def _phrase(raw: tuple[str, str, str], key: str, explanation_code: str) -> LearningPhrase:
    return LearningPhrase(phrase=raw[0], pronunciation=raw[1], meaning=_meaning_for(key, explanation_code, raw[2]))
