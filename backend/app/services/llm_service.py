import json
import re
import google.generativeai as genai
from typing import List, Dict, Any
from fastapi import HTTPException, status
from app.config import settings
from app.utils.prompts import get_question_generation_prompt, get_evaluation_prompt

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(settings.LLM_MODEL)


def _clean_json_response(raw: str) -> str:
    """Strip markdown code fences if present."""
    raw = raw.strip()
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return raw.strip()


def _parse_json_safe(raw: str) -> Dict[str, Any]:
    """Parse JSON with helpful error messaging."""
    cleaned = _clean_json_response(raw)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM returned invalid JSON: {str(e)}"
        )


def generate_questions(
    role: str,
    level: str,
    interview_type: str,
    difficulty: str,
    count: int
) -> List[Dict[str, str]]:
    """
    Calls Gemini to generate interview questions.
    Returns list of {question_text, category} dicts.
    """
    prompt = get_question_generation_prompt(
        role, level, interview_type, difficulty, count
    )

    try:
        response = model.generate_content(prompt)
        raw_text = response.text
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {str(e)}"
        )

    data = _parse_json_safe(raw_text)

    questions = data.get("questions", [])
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI returned no questions. Please try again."
        )

    for q in questions:
        if "question_text" not in q:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI returned malformed question structure."
            )

    return questions[:count]


def evaluate_answer(
    question_text: str,
    user_answer: str,
    role: str,
    level: str,
    interview_type: str
) -> Dict[str, Any]:
    """
    Calls Gemini to evaluate an answer on 5 axes.
    Returns evaluation dict with scores and feedback.
    """
    prompt = get_evaluation_prompt(
        question_text, user_answer, role, level, interview_type
    )

    try:
        response = model.generate_content(prompt)
        raw_text = response.text
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {str(e)}"
        )

    data = _parse_json_safe(raw_text)

    required_fields = [
        "technical_score", "depth_score", "clarity_score",
        "relevance_score", "structure_score", "strengths",
        "weaknesses", "improvement_suggestions"
    ]
    for field in required_fields:
        if field not in data:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI evaluation missing field: {field}"
            )

    # Clamp all scores to 0-10
    for score_field in [
        "technical_score", "depth_score", "clarity_score",
        "relevance_score", "structure_score"
    ]:
        data[score_field] = max(0.0, min(10.0, float(data[score_field])))

    return data