from datetime import UTC, datetime, timedelta

from app.models.word import ReviewGrade, SrsData


def schedule_review(srs: SrsData, grade: ReviewGrade) -> SrsData:
    now = datetime.now(UTC)

    if grade == ReviewGrade.FORGOT:
        srs.lapses += 1
        srs.repetitions = 0
        srs.ease_factor = max(130, srs.ease_factor - 20)
        srs.interval_minutes = 10 if srs.lapses == 1 else 8 * 60
    else:
        srs.repetitions += 1
        srs.ease_factor = min(300, srs.ease_factor + 8)
        if srs.repetitions == 1:
            srs.interval_minutes = 8 * 60
        elif srs.repetitions == 2:
            srs.interval_minutes = 24 * 60
        else:
            scaled_days = max(1, round((srs.interval_minutes / (24 * 60)) * (srs.ease_factor / 100)))
            srs.interval_minutes = scaled_days * 24 * 60

    srs.last_grade = grade
    srs.due_at = now + timedelta(minutes=srs.interval_minutes)
    return srs
