from dataclasses import dataclass

from app.schemas.grammar import GrammarCheckResponse, GrammarDrop, GrammarExample, GrammarExercise, GrammarTopic


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


def grammar_topics_for_tags(tags: set[str]) -> list[GrammarTopic]:
    return [_to_topic(topic, topic.tag in tags) for topic in sorted(TOPICS, key=lambda item: (item.tag not in tags, item.id))]


def check_grammar_answer(topic_id: str, exercise_id: str, answer: str) -> GrammarCheckResponse:
    topic = next((item for item in TOPICS if item.id == topic_id), None)
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
        feedback=exercise.explanation if correct else f"Майже. Правильний варіант: {exercise.answer}. {exercise.explanation}",
        score_delta=12 if correct else 2,
    )


def drops_for_tags(tags: set[str]) -> list[GrammarDrop]:
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


def _normalize_answer(value: str) -> str:
    return " ".join(value.strip().lower().rstrip(".!?").split())
