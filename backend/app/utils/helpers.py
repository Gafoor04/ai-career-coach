from typing import Optional


def calculate_overall_score(
    technical: float,
    depth: float,
    clarity: float,
    relevance: float,
    structure: float
) -> float:
    """
    Weighted score calculation:
    Technical: 30%, Depth: 25%, Clarity: 20%, Relevance: 15%, Structure: 10%
    """
    weighted = (
        technical * 0.30 +
        depth * 0.25 +
        clarity * 0.20 +
        relevance * 0.15 +
        structure * 0.10
    )
    return round(weighted, 2)


def get_rating(score: float) -> tuple[str, str]:
    """Returns (rating_code, rating_label) based on overall score."""
    if score >= 8.5:
        return "excellent", "Excellent — You're ready to apply!"
    elif score >= 7.0:
        return "good", "Good — Solid performance with minor gaps"
    elif score >= 5.0:
        return "needs_improvement", "Needs Improvement — Core understanding present, depth lacking"
    else:
        return "poor", "Poor — Significant preparation needed"


def get_rating_from_score(score: Optional[float]) -> Optional[str]:
    if score is None:
        return None
    rating, _ = get_rating(score)
    return rating