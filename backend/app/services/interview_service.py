import uuid
from datetime import datetime
from typing import Optional
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
    time_per_question: Optional[int],
    mode: str = "interview"
) -> models.InterviewSession:

    user = db.query(models.User).filter(models.User.id == user_id).first()
    print("CREATING SESSION MODE:", mode)

    weak_topics = user.weak_topics if user else []
    strong_topics = user.strong_topics if user else []

    raw_questions = llm_service.generate_questions(
        role=role,
        level=level,
        interview_type=interview_type,
        difficulty=difficulty,
        count=question_count,
        weak_topics=weak_topics,
        strong_topics=strong_topics,
        mode=mode
    )

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
        mode=mode
    )

    db.add(session)
    db.flush()

    for idx, q_data in enumerate(raw_questions):
        question = models.InterviewQuestion(
            session_id=session.id,
            question_index=idx,
            question_text=q_data["question_text"],
            category=q_data.get("category"),
            hint_level_1=q_data.get("hint_level_1"),
            hint_level_2=q_data.get("hint_level_2"),
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

    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.id == session_id,
        models.InterviewSession.user_id == user_id
    ).first()
    print("SESSION MODE:", session.mode)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status == models.SessionStatus.completed:
        raise HTTPException(status_code=400, detail="Session already completed")

    question = db.query(models.InterviewQuestion).filter(
        models.InterviewQuestion.id == question_id,
        models.InterviewQuestion.session_id == session_id
    ).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    if question.user_answer is not None:
        raise HTTPException(status_code=400, detail="Question already answered")

    # =========================
    # 🔥 FINAL MODE (STRICT PATH)
    # =========================
    if session.mode == "final":

        evaluation = llm_service.evaluate_answer(
            question_text=question.question_text,
            user_answer=answer,
            role=session.role,
            level=session.level,
            interview_type=session.interview_type,
            mode="final"   # 👈 IMPORTANT
        )

        overall = calculate_overall_score(
            technical=evaluation["technical_score"],
            depth=evaluation["depth_score"],
            clarity=evaluation["clarity_score"],
            relevance=evaluation["relevance_score"],
            structure=evaluation["structure_score"]
        )

        # ✅ SAVE ANSWER (same as before)
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

        db.commit()

        # 🔥 NEXT QUESTION ONLY (NO FOLLOW-UP EXIST HERE)
        answered_count = db.query(models.InterviewQuestion).filter(
            models.InterviewQuestion.session_id == session_id,
            models.InterviewQuestion.user_answer.isnot(None)
        ).count()

        next_question = db.query(models.InterviewQuestion).filter(
            models.InterviewQuestion.session_id == session_id,
            models.InterviewQuestion.user_answer.is_(None)
        ).order_by(models.InterviewQuestion.question_index).first()

        is_last = answered_count >= session.question_count

        if is_last:
            session.status = models.SessionStatus.completed
            session.total_score = scoring_service.compute_session_score(session.questions)
            session.completed_at = datetime.utcnow()
            db.commit()

        return evaluation, overall, next_question, is_last, answered_count

    # =========================
    # 🔥 NORMAL MODE EVALUATION (ADD THIS)
    # =========================

    evaluation = llm_service.evaluate_answer(
        question_text=question.question_text,
        user_answer=answer,
        role=session.role,
        level=session.level,
        interview_type=session.interview_type,
        mode=session.mode
    )

    overall = calculate_overall_score(
        technical=evaluation["technical_score"],
        depth=evaluation["depth_score"],
        clarity=evaluation["clarity_score"],
        relevance=evaluation["relevance_score"],
        structure=evaluation["structure_score"]
    )

    # SAVE ANSWER
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

    # MEMORY UPDATE
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        weak_topics = evaluation.get("weak_topics", [])
        strong_topics = evaluation.get("strong_topics", [])

        user.weak_topics = list(set((user.weak_topics or []) + weak_topics))
        user.strong_topics = list(set((user.strong_topics or []) + strong_topics))
        user.interview_count = (user.interview_count or 0) + 1

    db.commit()

    # NOW count answers
    answered_count = db.query(models.InterviewQuestion).filter(
        models.InterviewQuestion.session_id == session_id,
        models.InterviewQuestion.user_answer.isnot(None)
    ).count()

   

    # =========================
    # 🔥 NORMAL MODE
    # =========================
    FOLLOWUP_THRESHOLD = 5.0

    should_followup = (
        overall < FOLLOWUP_THRESHOLD and not question.is_followup
    )

    if should_followup:
        followup_data = llm_service.generate_followup_question(
            original_question=question.question_text,
            user_answer=answer,
            weaknesses=evaluation["weaknesses"],
            role=session.role,
            level=session.level,
            mode=session.mode
        )

        followup = models.InterviewQuestion(
            session_id=session_id,
            question_index=question.question_index + 0.5,
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
        is_last = False

    else:
        next_question = db.query(models.InterviewQuestion).filter(
            models.InterviewQuestion.session_id == session_id,
            models.InterviewQuestion.user_answer.is_(None)
        ).order_by(models.InterviewQuestion.question_index).first()

        is_last = answered_count >= session.question_count

        if is_last:
            session.status = models.SessionStatus.completed
            session.total_score = scoring_service.compute_session_score(session.questions)
            session.completed_at = datetime.utcnow()

    db.commit()

    return evaluation, overall, next_question, is_last, answered_count


def get_session_summary(db: Session, session_id: uuid.UUID, user_id: uuid.UUID):

    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.id == session_id,
        models.InterviewSession.user_id == user_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    total_score = session.total_score or scoring_service.compute_session_score(session.questions) or 0.0
    rating_code, rating_label = get_rating(total_score)
    axis_averages = scoring_service.compute_axis_averages(session.questions)
    weak_areas = scoring_service.get_weak_areas(session.questions)

    verdict = "No Hire"
    if total_score >= 8:
        verdict = "Strong Hire"
    elif total_score >= 6.5:
        verdict = "Hire"
    elif total_score >= 5:
        verdict = "Borderline"

    return {
        "session_id": session.id,
        "role": session.role,
        "level": session.level,
        "interview_type": session.interview_type,
        "difficulty": session.difficulty,
        "total_score": total_score,
        "verdict": verdict,
        "rating": rating_code,
        "rating_label": rating_label,
        "axis_averages": axis_averages,
        "questions": session.questions,
        "weak_areas": weak_areas,
        "created_at": session.created_at,
        "completed_at": session.completed_at,
    }