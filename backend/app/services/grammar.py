from app.schemas.grammar import GrammarDrop


def detect_mistake_tag(text: str) -> str | None:
    clean = f" {text.lower()} "
    past_markers = (" yesterday", " last night", " last week", " in 202", " ago")
    present_perfect_markers = (" have ", " has ")
    irregular_slips = (" have went", " has went", " have saw", " has saw", " have did", " has did")

    if any(marker in clean for marker in past_markers) and any(marker in clean for marker in present_perfect_markers):
        return "past_simple_vs_present_perfect"
    if any(slip in clean for slip in irregular_slips):
        return "past_simple_vs_present_perfect"
    return None


def drops_for_tags(tags: set[str]) -> list[GrammarDrop]:
    if "past_simple_vs_present_perfect" in tags:
        return [
            GrammarDrop(
                id="present-perfect-rescue",
                title="Perfect Rescue",
                nudge="Present Perfect is getting noisy. Tiny reset, no drama?",
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
