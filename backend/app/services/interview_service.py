import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import models
from app.services import llm_service, scoring_service
from app.utils.helpers import calculate_overall_score, get_rating


def create_session_with_questions(
    db: Session,
    user_id: uuid.UUID,
    role: str,
    level: str,
    interview_type: str,
    difficulty: str,
    question_count: int,
    timer_enabled: bool,
    time_per_question: Optional[int]
) -> models.InterviewSession:
    """Generate questions via LLM and create session in DB."""

    # 1. Generate questions via LLM
    raw_questions = llm_service.generate_questions(
        role=role,
        level=level,
        interview_type=interview_type,
        difficulty=difficulty,
        count=question_count
    )

    # 2. Create session
    session = models.InterviewSession(
        user_id=user_id,
        role=role,
        level=level,
        interview_type=interview_type,
        difficulty=difficulty,
        question_count=len(raw_questions),
        timer_enabled=timer_enabled,
        time_per_question=time_per_question,
        status=models.SessionStatus.in_progress,
    )
    db.add(session)
    db.flush()  # Get session.id before creating questions

    # 3. Create question records
    for idx, q_data in enumerate(raw_questions):
        question = models.InterviewQuestion(
            session_id=session.id,
            question_index=idx,
            question_text=q_data["question_text"],
            category=q_data.get("category"),
        )
        db.add(question)

    db.commit()
    db.refresh(session)
    return session


def submit_answer_and_evaluate(
    db: Session,
    session_id: uuid.UUID,
    question_id: uuid.UUID,
    user_id: uuid.UUID,
    answer: str
):
    """Evaluate an answer, store scores, return result + next question."""

    # 1. Validate session belongs to user
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.id == session_id,
        models.InterviewSession.user_id == user_id
    ).first()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if session.status == models.SessionStatus.completed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session already completed")

    # 2. Validate question belongs to session
    question = db.query(models.InterviewQuestion).filter(
        models.InterviewQuestion.id == question_id,
        models.InterviewQuestion.session_id == session_id
    ).first()

    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    if question.user_answer is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question already answered")

    # 3. Evaluate via LLM
    evaluation = llm_service.evaluate_answer(
        question_text=question.question_text,
        user_answer=answer,
        role=session.role,
        level=session.level,
        interview_type=session.interview_type
    )

    # 4. Calculate weighted overall score
    overall = calculate_overall_score(
        technical=evaluation["technical_score"],
        depth=evaluation["depth_score"],
        clarity=evaluation["clarity_score"],
        relevance=evaluation["relevance_score"],
        structure=evaluation["structure_score"]
    )

    # 5. Update question record
    question.user_answer = answer
    question.technical_score = evaluation["technical_score"]
    question.depth_score = evaluation["depth_score"]
    question.clarity_score = evaluation["clarity_score"]
    question.relevance_score = evaluation["relevance_score"]
    question.structure_score = evaluation["structure_score"]
    question.overall_score = overall
    question.strengths = evaluation["strengths"]
    question.weaknesses = evaluation["weaknesses"]
    question.improvement_suggestions = evaluation["improvement_suggestions"]
    question.answered_at = datetime.utcnow()
    db.flush()

    # 6. Check if this was the last question
    answered_count = db.query(models.InterviewQuestion).filter(
        models.InterviewQuestion.session_id == session_id,
        models.InterviewQuestion.user_answer.isnot(None)
    ).count()

    next_question = None
    is_last = answered_count >= session.question_count

    if is_last:
        # Mark session complete and calculate total score
        all_questions = session.questions
        session.status = models.SessionStatus.completed
        session.total_score = scoring_service.compute_session_score(all_questions)
        session.completed_at = datetime.utcnow()
    else:
        # Get next unanswered question
        next_question = db.query(models.InterviewQuestion).filter(
            models.InterviewQuestion.session_id == session_id,
            models.InterviewQuestion.user_answer.is_(None)
        ).order_by(models.InterviewQuestion.question_index).first()

    db.commit()

    return evaluation, overall, next_question, is_last, answered_count


def get_session_summary(
    db: Session,
    session_id: uuid.UUID,
    user_id: uuid.UUID
):
    """Build full session summary for result page."""
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.id == session_id,
        models.InterviewSession.user_id == user_id
    ).first()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    total_score = session.total_score or scoring_service.compute_session_score(session.questions) or 0.0
    rating_code, rating_label = get_rating(total_score)
    axis_averages = scoring_service.compute_axis_averages(session.questions)
    weak_areas = scoring_service.get_weak_areas(session.questions)

    return {
        "session_id": session.id,
        "role": session.role,
        "level": session.level,
        "interview_type": session.interview_type,
        "difficulty": session.difficulty,
        "total_score": total_score,
        "rating": rating_code,
        "rating_label": rating_label,
        "axis_averages": axis_averages,
        "questions": session.questions,
        "weak_areas": weak_areas,
        "created_at": session.created_at,
        "completed_at": session.completed_at,
    }