from dataclasses import dataclass, replace

from app.core.languages import language_name, normalize_language_code
from app.schemas.grammar import GrammarCheckResponse, GrammarDrop, GrammarExample, GrammarExercise, GrammarTopic
from app.services.language_course import MEANING_TRANSLATIONS, starter_pack


@dataclass(frozen=True)
class GrammarExerciseSpec:
    id: str
    type: str
    prompt: str
    answer: str
    explanation: str
    options: tuple[str, ...] = ()
    accepted: tuple[str, ...] = ()


@dataclass(frozen=True)
class GrammarTopicSpec:
    id: str
    tag: str
    title: str
    level: str
    summary: str
    micro_lesson: str
    rules: tuple[str, ...]
    examples: tuple[GrammarExample, ...]
    exercises: tuple[GrammarExerciseSpec, ...]
    reason: str


TOPICS: tuple[GrammarTopicSpec, ...] = (
    GrammarTopicSpec(
        id="past-simple-present-perfect",
        tag="past_simple_vs_present_perfect",
        title="Past Simple vs Present Perfect",
        level="A2-B1",
        summary="Розділяємо завершений час і результат, який важливий зараз.",
        micro_lesson=(
            "Past Simple відповідає на питання WHEN: yesterday, last week, in 2024. "
            "Present Perfect відповідає WHAT NOW: experience, result, already/just/yet."
        ),
        rules=(
            "Є точний завершений час -> Past Simple.",
            "Немає точного часу, важливий результат зараз -> Present Perfect.",
            "Після yesterday/last/ago не ставимо have/has.",
        ),
        examples=(
            GrammarExample(wrong="I have seen it yesterday.", right="I saw it yesterday.", note="yesterday закриває дію у минулому."),
            GrammarExample(wrong=None, right="I have already seen it.", note="already показує результат: мені вже не треба дивитись."),
        ),
        exercises=(
            GrammarExerciseSpec(
                id="pspp-1",
                type="choice",
                prompt="Yesterday I ___ Alex at the cafe.",
                answer="saw",
                options=("saw", "have seen", "has seen"),
                explanation="Yesterday = точний завершений час, тому Past Simple: saw.",
            ),
            GrammarExerciseSpec(
                id="pspp-2",
                type="choice",
                prompt="I ___ this song three times already.",
                answer="have heard",
                options=("heard", "have heard", "has heard"),
                explanation="Already + досвід до зараз = Present Perfect: have heard.",
            ),
            GrammarExerciseSpec(
                id="pspp-3",
                type="transform",
                prompt="Fix it: I have went to the cafe last night.",
                answer="I went to the cafe last night.",
                accepted=("I went to the cafe last night",),
                explanation="Last night забирає have, а went вже є Past Simple.",
            ),
        ),
        reason="Твій AI-тьютор бачив плутанину часів у спікінгу, тому ця тема зараз перша.",
    ),
    GrammarTopicSpec(
        id="articles-a-an-the",
        tag="articles",
        title="A / An / The",
        level="A1-A2",
        summary="Наводимо порядок у артиклях без сухого підручника.",
        micro_lesson=(
            "A/an означає новий або будь-який предмет. The означає конкретний предмет, який вже зрозумілий з контексту."
        ),
        rules=(
            "A перед приголосним звуком: a coffee, a user.",
            "An перед голосним звуком: an apple, an hour.",
            "The, коли предмет вже відомий або єдиний у ситуації.",
        ),
        examples=(
            GrammarExample(wrong="I need the coffee.", right="I need a coffee.", note="Ти просиш будь-яку каву, не конкретну."),
            GrammarExample(wrong=None, right="The coffee you made is perfect.", note="Тут кава вже конкретна."),
        ),
        exercises=(
            GrammarExerciseSpec(
                id="art-1",
                type="choice",
                prompt="Can I get ___ oat latte?",
                answer="an",
                options=("a", "an", "the"),
                explanation="Oat починається з голосного звуку, тому an.",
            ),
            GrammarExerciseSpec(
                id="art-2",
                type="choice",
                prompt="___ latte you made yesterday was amazing.",
                answer="The",
                options=("A", "An", "The"),
                explanation="Йдеться про конкретне latte з учора, тому The.",
            ),
            GrammarExerciseSpec(
                id="art-3",
                type="transform",
                prompt="Fix it: She is an developer.",
                answer="She is a developer.",
                accepted=("She is a developer",),
                explanation="Developer починається з приголосного звуку, тому a.",
            ),
        ),
        reason="AI помітив артиклі як слабке місце, тренуємо їх коротко і прикладно.",
    ),
    GrammarTopicSpec(
        id="prepositions-time-place",
        tag="prepositions",
        title="In / On / At",
        level="A1-A2",
        summary="Час і місце без хаосу: in, on, at як три масштаби.",
        micro_lesson="In = всередині великого періоду/простору. On = поверхня або день. At = точка, адреса, точний час.",
        rules=(
            "In: in May, in the morning, in Kyiv.",
            "On: on Monday, on the table, on my phone.",
            "At: at 8 PM, at home, at the station.",
        ),
        examples=(
            GrammarExample(wrong="I will call you in Monday.", right="I will call you on Monday.", note="Дні тижня беруть on."),
            GrammarExample(wrong=None, right="Meet me at 8 PM.", note="Точний час = at."),
        ),
        exercises=(
            GrammarExerciseSpec(
                id="prep-1",
                type="choice",
                prompt="Let's meet ___ 7 PM.",
                answer="at",
                options=("in", "on", "at"),
                explanation="7 PM = точний час, тому at.",
            ),
            GrammarExerciseSpec(
                id="prep-2",
                type="choice",
                prompt="I have an interview ___ Friday.",
                answer="on",
                options=("in", "on", "at"),
                explanation="День тижня = on.",
            ),
            GrammarExerciseSpec(
                id="prep-3",
                type="transform",
                prompt="Fix it: I live at Warsaw.",
                answer="I live in Warsaw.",
                accepted=("I live in Warsaw",),
                explanation="Місто як простір = in.",
            ),
        ),
        reason="Після помилок з прийменниками ця тема піднімається першою.",
    ),
    GrammarTopicSpec(
        id="conditionals-real-future",
        tag="conditionals",
        title="Real Future: If + Present",
        level="B1",
        summary="Реальні умови майбутнього без if I will.",
        micro_lesson="У реальній майбутній умові після if ставимо Present Simple, а will лишаємо у другій частині.",
        rules=(
            "If + Present Simple, will + verb.",
            "Не кажемо if I will have time.",
            "Порядок частин можна міняти: I will call if I have time.",
        ),
        examples=(
            GrammarExample(wrong="If I will have time, I will call.", right="If I have time, I will call.", note="Після if не треба will."),
            GrammarExample(wrong=None, right="I will text you if I finish early.", note="Will стоїть у результаті, не в умові."),
        ),
        exercises=(
            GrammarExerciseSpec(
                id="cond-1",
                type="choice",
                prompt="If she ___ free, she will join us.",
                answer="is",
                options=("will be", "is", "would be"),
                explanation="Після if для реального майбутнього ставимо Present Simple.",
            ),
            GrammarExerciseSpec(
                id="cond-2",
                type="transform",
                prompt="Fix it: If I will finish early, I will text you.",
                answer="If I finish early, I will text you.",
                accepted=("If I finish early, I will text you",),
                explanation="Умова після if: finish, не will finish.",
            ),
            GrammarExerciseSpec(
                id="cond-3",
                type="choice",
                prompt="I will go for a walk if it ___ raining.",
                answer="stops",
                options=("will stop", "stops", "stopped"),
                explanation="Реальна умова майбутнього: if it stops.",
            ),
        ),
        reason="AI помітив if/will патерн, тому тренуємо саме живі умови.",
    ),
)


STARTER_GRAMMAR_COPY: dict[str, dict[str, str]] = {
    "uk": {
        "starter_title": "{name}: перші фрази",
        "starter_summary": "Стартуємо {name} з готових живих фраз, а не з таблиці правил.",
        "starter_lesson": (
            "Новачку спочатку потрібні мовні блоки: привітатись, попросити щось, подякувати. "
            "Граматика підтягується після того, як фраза вже звучить у роті."
        ),
        "starter_rule_1": "Не перекладай слово в слово, бери фразу як готовий шаблон.",
        "starter_rule_2": "Повтори фразу вголос 2-3 рази, навіть якщо вимова ще не ідеальна.",
        "starter_rule_3": "У спікінгу AI буде відповідати цією ж мовою і просити коротку реакцію.",
        "example_note": "Вимова: {pronunciation}. Значення: {meaning}",
        "hello_prompt": "Обери фразу для: «Привіт, я Саша».",
        "hello_explanation": "Це базове представлення у {name}: {phrase}",
        "thanks_prompt": "Обери фразу, яка звучить як ввічливе «дякую / добре».",
        "thanks_explanation": "Ця фраза закриває міні-діалог: {phrase}",
        "starter_reason": "Ти вчиш {name}, тому починаємо з готових фраз для першої розмови.",
        "requests_title": "{name}: попросити щось",
        "requests_summary": "Перша практична конструкція: як попросити каву, допомогу або повторення.",
        "requests_lesson": "У більшості мов ввічливість живе не в одному слові, а у всій фразі. Запам'ятай її блоком.",
        "request_rule_1": "Фраза-заготовка: {phrase}",
        "request_rule_2": "Після неї можна міняти предмет: кава, вода, квиток, допомога.",
        "request_rule_3": "Якщо зависла, попроси допомогу готовим питанням.",
        "meaning_note": "Значення: {meaning}",
        "want_prompt": "Що сказати, якщо хочеш каву?",
        "want_explanation": "Для прохання використовуй: {phrase}",
        "question_prompt": "Що сказати, коли треба попросити допомогу?",
        "question_explanation": "Це готове питання для допомоги: {phrase}",
        "requests_reason": "AI-тьютор буде тренувати прохання у {name}, бо це найшвидше дає відчуття «я можу говорити».",
        "drop_nudge": "Починаємо {name} з фрази, яку реально можна сказати вголос.",
        "drop_tiny": "Скажи: {hello} Потім попроси щось: {want}",
    },
    "ru": {
        "starter_title": "{name}: первые фразы",
        "starter_summary": "Начинаем {name} с готовых живых фраз, а не с таблицы правил.",
        "starter_lesson": (
            "Новичку сначала нужны речевые блоки: поздороваться, попросить что-то, поблагодарить. "
            "Грамматика подтягивается после того, как фраза уже звучит во рту."
        ),
        "starter_rule_1": "Не переводи слово в слово, бери фразу как готовый шаблон.",
        "starter_rule_2": "Повтори фразу вслух 2-3 раза, даже если произношение еще не идеальное.",
        "starter_rule_3": "В спикинге AI будет отвечать на этом же языке и просить короткую реакцию.",
        "example_note": "Произношение: {pronunciation}. Значение: {meaning}",
        "hello_prompt": "Выбери фразу для: «Привет, я Саша».",
        "hello_explanation": "Это базовое представление в {name}: {phrase}",
        "thanks_prompt": "Выбери фразу, которая звучит как вежливое «спасибо / хорошо».",
        "thanks_explanation": "Эта фраза закрывает мини-диалог: {phrase}",
        "starter_reason": "Ты учишь {name}, поэтому начинаем с готовых фраз для первого разговора.",
        "requests_title": "{name}: попросить что-то",
        "requests_summary": "Первая практичная конструкция: как попросить кофе, помощь или повторение.",
        "requests_lesson": "В большинстве языков вежливость живет не в одном слове, а во всей фразе. Запомни ее блоком.",
        "request_rule_1": "Фраза-заготовка: {phrase}",
        "request_rule_2": "После нее можно менять предмет: кофе, вода, билет, помощь.",
        "request_rule_3": "Если зависла, попроси помощь готовым вопросом.",
        "meaning_note": "Значение: {meaning}",
        "want_prompt": "Что сказать, если хочешь кофе?",
        "want_explanation": "Для просьбы используй: {phrase}",
        "question_prompt": "Что сказать, когда нужно попросить помощь?",
        "question_explanation": "Это готовый вопрос для помощи: {phrase}",
        "requests_reason": "AI-тьютор будет тренировать просьбы в {name}, потому что это быстрее всего дает ощущение «я могу говорить».",
        "drop_nudge": "Начинаем {name} с фразы, которую реально можно сказать вслух.",
        "drop_tiny": "Скажи: {hello} Потом попроси что-то: {want}",
    },
    "en": {
        "starter_title": "{name}: first phrases",
        "starter_summary": "We start {name} with useful ready phrases, not a dry rules table.",
        "starter_lesson": (
            "A beginner first needs language chunks: greet someone, ask for something, say thanks. "
            "Grammar comes after the phrase already feels speakable."
        ),
        "starter_rule_1": "Do not translate word by word; treat the phrase as a ready template.",
        "starter_rule_2": "Repeat it out loud 2-3 times, even if pronunciation is not perfect yet.",
        "starter_rule_3": "In Speaking, AI will answer in the same language and ask for a short reaction.",
        "example_note": "Pronunciation: {pronunciation}. Meaning: {meaning}",
        "hello_prompt": "Choose the phrase for: \"Hi, I'm Sasha.\"",
        "hello_explanation": "This is a basic introduction in {name}: {phrase}",
        "thanks_prompt": "Choose the phrase that works like polite \"thanks / okay\".",
        "thanks_explanation": "This phrase closes a tiny dialogue: {phrase}",
        "starter_reason": "You are learning {name}, so we start with ready phrases for the first conversation.",
        "requests_title": "{name}: ask for something",
        "requests_summary": "The first practical pattern: asking for coffee, help, or repetition.",
        "requests_lesson": "In most languages, politeness lives in the whole phrase, not in one magic word. Learn it as a chunk.",
        "request_rule_1": "Ready phrase: {phrase}",
        "request_rule_2": "After it, you can swap the object: coffee, water, ticket, help.",
        "request_rule_3": "If you freeze, ask for help with a ready question.",
        "meaning_note": "Meaning: {meaning}",
        "want_prompt": "What do you say if you want coffee?",
        "want_explanation": "For a request, use: {phrase}",
        "question_prompt": "What do you say when you need to ask for help?",
        "question_explanation": "This is a ready help question: {phrase}",
        "requests_reason": "The AI tutor will train requests in {name}, because this gives the fastest feeling of \"I can speak\".",
        "drop_nudge": "We start {name} with a phrase you can actually say out loud.",
        "drop_tiny": "Say: {hello} Then ask for something: {want}",
    },
}


ENGLISH_GRAMMAR_COPY: dict[str, dict[str, dict[str, object]]] = {
    "en": {
        "past-simple-present-perfect": {
            "summary": "Separate finished time from a result that still matters now.",
            "micro_lesson": (
                "Past Simple answers WHEN: yesterday, last week, in 2024. "
                "Present Perfect answers WHAT NOW: experience, result, already/just/yet."
            ),
            "rules": (
                "A named finished time -> Past Simple.",
                "No exact time and the result matters now -> Present Perfect.",
                "After yesterday/last/ago, do not use have/has.",
            ),
            "notes": (
                "yesterday closes the action in the past.",
                "already shows a result: I do not need to watch it again.",
            ),
            "explanations": (
                "Yesterday = exact finished time, so Past Simple: saw.",
                "Already + experience up to now = Present Perfect: have heard.",
                "Last night removes have, and went is already Past Simple.",
            ),
            "reason": "Your AI tutor noticed tense confusion in speaking, so this topic comes first.",
        },
        "articles-a-an-the": {
            "summary": "Clean up articles without a dry textbook mood.",
            "micro_lesson": "A/an means a new or any item. The means a specific item that is clear from context.",
            "rules": (
                "A before a consonant sound: a coffee, a user.",
                "An before a vowel sound: an apple, an hour.",
                "The when the item is already known or unique in the situation.",
            ),
            "notes": (
                "You are asking for any coffee, not one specific coffee.",
                "Here the coffee is already specific.",
            ),
            "explanations": (
                "Oat starts with a vowel sound, so use an.",
                "This is the specific latte from yesterday, so use The.",
                "Developer starts with a consonant sound, so use a.",
            ),
            "reason": "AI marked articles as a weak spot, so we train them briefly and practically.",
        },
        "prepositions-time-place": {
            "summary": "Time and place without chaos: in, on, at as three scales.",
            "micro_lesson": "In = inside a larger period/place. On = surface or day. At = point, address, exact time.",
            "rules": (
                "In: in May, in the morning, in Kyiv.",
                "On: on Monday, on the table, on my phone.",
                "At: at 8 PM, at home, at the station.",
            ),
            "notes": (
                "Days of the week take on.",
                "Exact time = at.",
            ),
            "explanations": (
                "7 PM = exact time, so at.",
                "A day of the week = on.",
                "A city as a place/area = in.",
            ),
            "reason": "After preposition mistakes, this topic rises to the top.",
        },
        "conditionals-real-future": {
            "summary": "Real future conditions without if I will.",
            "micro_lesson": "In a real future condition, use Present Simple after if and keep will in the result clause.",
            "rules": (
                "If + Present Simple, will + verb.",
                "Do not say if I will have time.",
                "You can switch the order: I will call if I have time.",
            ),
            "notes": (
                "No will after if.",
                "Will belongs in the result, not the condition.",
            ),
            "explanations": (
                "After if in a real future condition, use Present Simple.",
                "The condition after if is finish, not will finish.",
                "Real future condition: if it stops.",
            ),
            "reason": "AI noticed an if/will pattern, so we train practical conditions.",
        },
    },
    "ru": {
        "past-simple-present-perfect": {
            "summary": "Разделяем завершенное время и результат, который важен сейчас.",
            "micro_lesson": (
                "Past Simple отвечает на WHEN: yesterday, last week, in 2024. "
                "Present Perfect отвечает WHAT NOW: experience, result, already/just/yet."
            ),
            "rules": (
                "Есть точное завершенное время -> Past Simple.",
                "Нет точного времени, важен результат сейчас -> Present Perfect.",
                "После yesterday/last/ago не ставим have/has.",
            ),
            "notes": (
                "yesterday закрывает действие в прошлом.",
                "already показывает результат: мне уже не нужно смотреть.",
            ),
            "explanations": (
                "Yesterday = точное завершенное время, поэтому Past Simple: saw.",
                "Already + опыт до сейчас = Present Perfect: have heard.",
                "Last night убирает have, а went уже Past Simple.",
            ),
            "reason": "Твой AI-тьютор заметил путаницу времен в спикинге, поэтому эта тема сейчас первая.",
        },
        "articles-a-an-the": {
            "summary": "Наводим порядок в артиклях без сухого учебника.",
            "micro_lesson": "A/an означает новый или любой предмет. The означает конкретный предмет, понятный из контекста.",
            "rules": (
                "A перед согласным звуком: a coffee, a user.",
                "An перед гласным звуком: an apple, an hour.",
                "The, когда предмет уже известен или единственный в ситуации.",
            ),
            "notes": (
                "Ты просишь любой кофе, не конкретный.",
                "Здесь кофе уже конкретный.",
            ),
            "explanations": (
                "Oat начинается с гласного звука, поэтому an.",
                "Речь про конкретное latte со вчера, поэтому The.",
                "Developer начинается с согласного звука, поэтому a.",
            ),
            "reason": "AI заметил артикли как слабое место, тренируем их коротко и прикладно.",
        },
        "prepositions-time-place": {
            "summary": "Время и место без хаоса: in, on, at как три масштаба.",
            "micro_lesson": "In = внутри большого периода/пространства. On = поверхность или день. At = точка, адрес, точное время.",
            "rules": (
                "In: in May, in the morning, in Kyiv.",
                "On: on Monday, on the table, on my phone.",
                "At: at 8 PM, at home, at the station.",
            ),
            "notes": (
                "Дни недели берут on.",
                "Точное время = at.",
            ),
            "explanations": (
                "7 PM = точное время, поэтому at.",
                "День недели = on.",
                "Город как пространство = in.",
            ),
            "reason": "После ошибок с предлогами эта тема поднимается первой.",
        },
        "conditionals-real-future": {
            "summary": "Реальные условия будущего без if I will.",
            "micro_lesson": "В реальном будущем условии после if ставим Present Simple, а will оставляем во второй части.",
            "rules": (
                "If + Present Simple, will + verb.",
                "Не говорим if I will have time.",
                "Порядок частей можно менять: I will call if I have time.",
            ),
            "notes": (
                "После if не нужно will.",
                "Will стоит в результате, не в условии.",
            ),
            "explanations": (
                "После if для реального будущего ставим Present Simple.",
                "Условие после if: finish, не will finish.",
                "Реальное условие будущего: if it stops.",
            ),
            "reason": "AI заметил if/will паттерн, поэтому тренируем живые условия.",
        },
    },
}


def beginner_topics(language_code: str, target_language_code: str = "uk") -> tuple[GrammarTopicSpec, ...]:
    code = normalize_language_code(language_code)
    if code == "en":
        return _english_topics(target_language_code)

    name = language_name(code)
    pack = starter_pack(code)
    hello, want, question, thanks = pack["hello"], pack["want"], pack["question"], pack["thanks"]
    copy = _starter_copy(target_language_code)
    hello_meaning = _starter_meaning("hello", target_language_code, hello[2])
    want_meaning = _starter_meaning("want", target_language_code, want[2])
    question_meaning = _starter_meaning("question", target_language_code, question[2])
    thanks_meaning = _starter_meaning("thanks", target_language_code, thanks[2])

    return (
        GrammarTopicSpec(
            id=f"{code}-starter-phrases",
            tag="starter_phrases",
            title=copy["starter_title"].format(name=name),
            level="A0",
            summary=copy["starter_summary"].format(name=name),
            micro_lesson=copy["starter_lesson"],
            rules=(
                copy["starter_rule_1"],
                copy["starter_rule_2"],
                copy["starter_rule_3"],
            ),
            examples=(
                GrammarExample(wrong=None, right=hello[0], note=copy["example_note"].format(pronunciation=hello[1], meaning=hello_meaning)),
                GrammarExample(wrong=None, right=thanks[0], note=copy["example_note"].format(pronunciation=thanks[1], meaning=thanks_meaning)),
            ),
            exercises=(
                GrammarExerciseSpec(
                    id=f"{code}-starter-1",
                    type="choice",
                    prompt=copy["hello_prompt"],
                    answer=hello[0],
                    options=(hello[0], want[0], question[0]),
                    explanation=copy["hello_explanation"].format(name=name, phrase=hello[0]),
                ),
                GrammarExerciseSpec(
                    id=f"{code}-starter-2",
                    type="choice",
                    prompt=copy["thanks_prompt"],
                    answer=thanks[0],
                    options=(question[0], thanks[0], want[0]),
                    explanation=copy["thanks_explanation"].format(phrase=thanks[0]),
                ),
            ),
            reason=copy["starter_reason"].format(name=name),
        ),
        GrammarTopicSpec(
            id=f"{code}-requests",
            tag="requests",
            title=copy["requests_title"].format(name=name),
            level="A0-A1",
            summary=copy["requests_summary"],
            micro_lesson=copy["requests_lesson"],
            rules=(
                copy["request_rule_1"].format(phrase=want[0]),
                copy["request_rule_2"],
                copy["request_rule_3"],
            ),
            examples=(
                GrammarExample(wrong=None, right=want[0], note=copy["meaning_note"].format(meaning=want_meaning)),
                GrammarExample(wrong=None, right=question[0], note=copy["meaning_note"].format(meaning=question_meaning)),
            ),
            exercises=(
                GrammarExerciseSpec(
                    id=f"{code}-request-1",
                    type="choice",
                    prompt=copy["want_prompt"],
                    answer=want[0],
                    options=(thanks[0], want[0], hello[0]),
                    explanation=copy["want_explanation"].format(phrase=want[0]),
                ),
                GrammarExerciseSpec(
                    id=f"{code}-request-2",
                    type="choice",
                    prompt=copy["question_prompt"],
                    answer=question[0],
                    options=(question[0], thanks[0], want[0]),
                    explanation=copy["question_explanation"].format(phrase=question[0]),
                ),
            ),
            reason=copy["requests_reason"].format(name=name),
        ),
    )


def detect_mistake_tag(text: str) -> str | None:
    clean = f" {text.lower()} "
    past_markers = (" yesterday", " last night", " last week", " in 202", " ago")
    present_perfect_markers = (" have ", " has ")
    irregular_slips = (" have went", " has went", " have saw", " has saw", " have did", " has did")

    if any(marker in clean for marker in past_markers) and any(marker in clean for marker in present_perfect_markers):
        return "past_simple_vs_present_perfect"
    if any(slip in clean for slip in irregular_slips):
        return "past_simple_vs_present_perfect"
    if " a apple" in clean or " an developer" in clean or " an user" in clean:
        return "articles"
    if " in monday" in clean or " at monday" in clean or " at kyiv" in clean or " at warsaw" in clean:
        return "prepositions"
    if " if i will " in clean or " if we will " in clean or " if she will " in clean or " if he will " in clean:
        return "conditionals"
    return None


def grammar_topics_for_tags(tags: set[str], language_code: str = "en", target_language_code: str = "uk") -> list[GrammarTopic]:
    topics = beginner_topics(language_code, target_language_code)
    return [_to_topic(topic, topic.tag in tags) for topic in sorted(topics, key=lambda item: (item.tag not in tags, item.id))]


def check_grammar_answer(
    topic_id: str,
    exercise_id: str,
    answer: str,
    language_code: str = "en",
    target_language_code: str = "uk",
) -> GrammarCheckResponse:
    topic = next((item for item in beginner_topics(language_code, target_language_code) if item.id == topic_id), None)
    if topic is None:
        return GrammarCheckResponse(correct=False, expected="", feedback="Topic not found.", score_delta=0)

    exercise = next((item for item in topic.exercises if item.id == exercise_id), None)
    if exercise is None:
        return GrammarCheckResponse(correct=False, expected="", feedback="Exercise not found.", score_delta=0)

    normalized_answer = _normalize_answer(answer)
    accepted = {_normalize_answer(exercise.answer), *[_normalize_answer(item) for item in exercise.accepted]}
    correct = normalized_answer in accepted
    return GrammarCheckResponse(
        correct=correct,
        expected=exercise.answer,
        feedback=exercise.explanation if correct else _almost_feedback(exercise.answer, exercise.explanation, target_language_code),
        score_delta=12 if correct else 2,
    )


def drops_for_tags(tags: set[str], language_code: str = "en", target_language_code: str = "uk") -> list[GrammarDrop]:
    code = normalize_language_code(language_code)
    if code != "en":
        pack = starter_pack(code)
        name = language_name(code)
        copy = _starter_copy(target_language_code)
        return [
            GrammarDrop(
                id=f"{code}-starter-drop",
                title=f"{name} Starter",
                nudge=copy["drop_nudge"].format(name=name),
                tiny_explanation=copy["drop_tiny"].format(hello=pack["hello"][0], want=pack["want"][0]),
                quests=[pack["hello"][0], pack["want"][0], pack["question"][0]],
            ),
        ]

    if "past_simple_vs_present_perfect" in tags:
        return [
            GrammarDrop(
                id="present-perfect-rescue",
                title="Perfect Rescue",
                nudge="AI помітив, що Past Simple і Present Perfect трохи змішались у спікінгу.",
                tiny_explanation=(
                    "Use Present Perfect when the result matters now. Use Past Simple when the time is finished "
                    "and named, like yesterday or last night."
                ),
                quests=[
                    "I saw it yesterday",
                    "I have already seen it",
                    "She called me last night",
                ],
            ),
        ]

    if "articles" in tags:
        return [
            GrammarDrop(
                id="article-reset",
                title="Article Reset",
                nudge="AI помітив артиклі. Розкладемо a/an/the за 30 секунд.",
                tiny_explanation="A/an = новий або будь-який предмет. The = конкретний предмет, який вже зрозумілий.",
                quests=["a coffee", "an apple", "the coffee you made"],
            ),
        ]

    if "prepositions" in tags:
        return [
            GrammarDrop(
                id="preposition-map",
                title="Preposition Map",
                nudge="Прийменники часу/місця хочуть маленьку карту: in, on, at.",
                tiny_explanation="In = простір/період. On = день/поверхня. At = точка/точний час.",
                quests=["on Monday", "at 8 PM", "in Warsaw"],
            ),
        ]

    if "conditionals" in tags:
        return [
            GrammarDrop(
                id="if-present",
                title="If + Present",
                nudge="AI помітив if + will. Для реального майбутнього після if ставимо Present Simple.",
                tiny_explanation="If I have time, I will call. Не: If I will have time.",
                quests=["If I have time", "If she is free", "I will text you if I finish"],
            ),
        ]

    return [
        GrammarDrop(
            id="soft-past-simple",
            title="Past Simple",
            nudge="Past Simple is tapping the window for 30 seconds.",
            tiny_explanation=(
                "When the action is finished and you know when it happened, English usually wants Past Simple."
            ),
            quests=[
                "I watched it yesterday",
                "She called me last night",
                "We met in 2024",
            ],
        ),
    ]


def _to_topic(topic: GrammarTopicSpec, recommended: bool) -> GrammarTopic:
    return GrammarTopic(
        id=topic.id,
        tag=topic.tag,
        title=topic.title,
        level=topic.level,
        summary=topic.summary,
        micro_lesson=topic.micro_lesson,
        rules=list(topic.rules),
        examples=list(topic.examples),
        exercises=[
            GrammarExercise(
                id=exercise.id,
                type=exercise.type,
                prompt=exercise.prompt,
                options=list(exercise.options),
                explanation=exercise.explanation,
            )
            for exercise in topic.exercises
        ],
        recommended=recommended,
        reason=topic.reason if recommended else "",
    )


def _english_topics(target_language_code: str) -> tuple[GrammarTopicSpec, ...]:
    if target_language_code == "uk":
        return TOPICS

    localized = ENGLISH_GRAMMAR_COPY.get(target_language_code, ENGLISH_GRAMMAR_COPY["en"])
    topics: list[GrammarTopicSpec] = []
    for topic in TOPICS:
        copy = localized.get(topic.id)
        if copy is None:
            topics.append(topic)
            continue

        notes = tuple(copy["notes"])
        explanations = tuple(copy["explanations"])
        topics.append(
            replace(
                topic,
                summary=str(copy["summary"]),
                micro_lesson=str(copy["micro_lesson"]),
                rules=tuple(str(item) for item in copy["rules"]),
                examples=tuple(
                    replace(example, note=str(notes[index]))
                    for index, example in enumerate(topic.examples)
                ),
                exercises=tuple(
                    replace(exercise, explanation=str(explanations[index]))
                    for index, exercise in enumerate(topic.exercises)
                ),
                reason=str(copy["reason"]),
            )
        )
    return tuple(topics)


def _starter_copy(target_language_code: str) -> dict[str, str]:
    return STARTER_GRAMMAR_COPY.get(target_language_code, STARTER_GRAMMAR_COPY["en"])


def _starter_meaning(key: str, target_language_code: str, fallback: str) -> str:
    return MEANING_TRANSLATIONS.get(target_language_code, MEANING_TRANSLATIONS["en"]).get(key, fallback)


def _normalize_answer(value: str) -> str:
    return " ".join(value.strip().lower().rstrip(".!?").split())


def _almost_feedback(answer: str, explanation: str, target_language_code: str) -> str:
    if target_language_code == "uk":
        return f"Майже. Правильний варіант: {answer}. {explanation}"
    if target_language_code == "ru":
        return f"Почти. Правильный вариант: {answer}. {explanation}"
    return f"Almost. Correct answer: {answer}. {explanation}"
