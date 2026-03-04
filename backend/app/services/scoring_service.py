from typing import List, Optional
from app.models import InterviewQuestion
from app.utils.helpers import calculate_overall_score, get_rating


def compute_session_score(questions: List[InterviewQuestion]) -> Optional[float]:
    """Average overall_score across all answered questions."""
    answered = [q for q in questions if q.overall_score is not None]
    if not answered:
        return None
    total = sum(q.overall_score for q in answered)
    return round(total / len(answered), 2)


def compute_axis_averages(questions: List[InterviewQuestion]) -> dict:
    """Average each axis score across all answered questions."""
    answered = [q for q in questions if q.overall_score is not None]
    if not answered:
        return {"technical": 0, "depth": 0, "clarity": 0, "relevance": 0, "structure": 0}

    count = len(answered)
    return {
        "technical": round(sum(q.technical_score or 0 for q in answered) / count, 2),
        "depth": round(sum(q.depth_score or 0 for q in answered) / count, 2),
        "clarity": round(sum(q.clarity_score or 0 for q in answered) / count, 2),
        "relevance": round(sum(q.relevance_score or 0 for q in answered) / count, 2),
        "structure": round(sum(q.structure_score or 0 for q in answered) / count, 2),
    }


def get_weak_areas(questions: List[InterviewQuestion], threshold: float = 6.0) -> List[str]:
    """Return categories where average score is below threshold."""
    category_scores: dict = {}
    category_counts: dict = {}

    for q in questions:
        if q.overall_score is not None and q.category:
            cat = q.category
            category_scores[cat] = category_scores.get(cat, 0) + q.overall_score
            category_counts[cat] = category_counts.get(cat, 0) + 1

    weak = []
    for cat, total in category_scores.items():
        avg = total / category_counts[cat]
        if avg < threshold:
            weak.append(cat)

    return weak