from datetime import UTC, datetime, timedelta

from app.models.word import ReviewGrade, SrsData

PUBLIC_REVIEW_INTERVAL_MINUTES = 24 * 60


def schedule_review(srs: SrsData, grade: ReviewGrade) -> SrsData:
    now = datetime.now(UTC)

    if grade == ReviewGrade.FORGOT:
        srs.lapses += 1
        srs.repetitions = 0
    else:
        srs.repetitions += 1

    srs.interval_minutes = PUBLIC_REVIEW_INTERVAL_MINUTES
    srs.last_grade = grade
    srs.due_at = now + timedelta(minutes=srs.interval_minutes)
    return srs
