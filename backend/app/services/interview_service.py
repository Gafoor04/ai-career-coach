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
    FOLLOWUP_THRESHOLD = 5.0

# Check follow-up BEFORE deciding if last question
    should_followup = overall < FOLLOWUP_THRESHOLD and not question.is_followup

    if should_followup:
        is_last = False  # override — follow-up comes next
    else:
        is_last = answered_count >= session.question_count

    

    

    if is_last:
        session.status = models.SessionStatus.completed
        session.total_score = scoring_service.compute_session_score(session.questions)
        session.completed_at = datetime.utcnow()
    else:
        # Generate follow-up if answer was weak and no follow-up exists yet
        if overall < FOLLOWUP_THRESHOLD and not question.is_followup:
            followup_data = llm_service.generate_followup_question(
                original_question=question.question_text,
                user_answer=answer,
                weaknesses=evaluation["weaknesses"],
                role=session.role,
                level=session.level
            )
            # Insert follow-up right after current question
            followup = models.InterviewQuestion(
                session_id=session_id,
                question_index=question.question_index + 0.5,  # sits between current and next
                question_text=followup_data["question_text"],
                category=followup_data.get("category", question.category),
                is_followup=True,
                parent_question_id=question.id
            )
            db.add(followup)
            db.flush()
            session.question_count = db.query(models.InterviewQuestion).filter(
                models.InterviewQuestion.session_id == session_id
            ).count()
            next_question = followup
        else:
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
def get_interview_stats(
    db: Session,
    user_id: uuid.UUID
):
    """Compute full interview stats for a user."""

    all_sessions = db.query(models.InterviewSession).filter(
        models.InterviewSession.user_id == user_id
    ).order_by(models.InterviewSession.created_at.asc()).all()

    total = len(all_sessions)
    completed = [s for s in all_sessions if s.status == models.SessionStatus.completed]
    abandoned = [s for s in all_sessions if s.status == models.SessionStatus.abandoned]

    scores = [s.total_score for s in completed if s.total_score is not None]

    average_score = round(sum(scores) / len(scores), 2) if scores else None
    best_score = round(max(scores), 2) if scores else None
    worst_score = round(min(scores), 2) if scores else None

    # Most practiced role
    role_counts: dict = {}
    for s in all_sessions:
        role_counts[s.role] = role_counts.get(s.role, 0) + 1
    most_practiced_role = max(role_counts, key=role_counts.get) if role_counts else None

    # Score trend (completed sessions only, chronological)
    score_trend = [
        {
            "session_id": s.id,
            "role": s.role,
            "total_score": s.total_score,
            "created_at": s.created_at
        }
        for s in completed if s.total_score is not None
    ]

    # Average score by interview type
    type_scores: dict = {}
    type_counts: dict = {}
    for s in completed:
        if s.total_score is not None:
            t = s.interview_type
            type_scores[t] = type_scores.get(t, 0) + s.total_score
            type_counts[t] = type_counts.get(t, 0) + 1
    average_by_type = {
        t: round(type_scores[t] / type_counts[t], 2)
        for t in type_scores
    }

    # Average score by difficulty
    diff_scores: dict = {}
    diff_counts: dict = {}
    for s in completed:
        if s.total_score is not None:
            d = s.difficulty
            diff_scores[d] = diff_scores.get(d, 0) + s.total_score
            diff_counts[d] = diff_counts.get(d, 0) + 1
    average_by_difficulty = {
        d: round(diff_scores[d] / diff_counts[d], 2)
        for d in diff_scores
    }

    return {
        "total_interviews": total,
        "completed_interviews": len(completed),
        "abandoned_interviews": len(abandoned),
        "average_score": average_score,
        "best_score": best_score,
        "worst_score": worst_score,
        "most_practiced_role": most_practiced_role,
        "score_trend": score_trend,
        "average_by_type": average_by_type,
        "average_by_difficulty": average_by_difficulty,
    }
