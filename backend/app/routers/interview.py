from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app import models, schemas
from app.utils.auth import get_current_user
from app.services import interview_service
from app.utils.helpers import get_rating_from_score
import math

router = APIRouter(prefix="/interview", tags=["Interview"])


@router.post("/start", response_model=schemas.InterviewStartResponse)
def start_interview(
    request: schemas.InterviewStartRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    session = interview_service.create_session_with_questions(
        db=db,
        user_id=current_user.id,
        role=request.role,
        level=request.level,
        interview_type=request.interview_type,
        difficulty=request.difficulty,
        question_count=request.question_count,
        timer_enabled=request.timer_enabled,
        time_per_question=request.time_per_question
    )
    first_question = session.questions[0]
    return schemas.InterviewStartResponse(
        session_id=session.id,
        first_question=schemas.QuestionOut.from_orm(first_question),
        total_questions=session.question_count
    )


@router.post("/answer", response_model=schemas.AnswerSubmitResponse)
def submit_answer(
    request: schemas.AnswerSubmitRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    evaluation, overall_score, next_question, is_last, answered_count = \
        interview_service.submit_answer_and_evaluate(
            db=db,
            session_id=request.session_id,
            question_id=request.question_id,
            user_id=current_user.id,
            answer=request.answer
        )

    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.id == request.session_id
    ).first()

    return schemas.AnswerSubmitResponse(
        evaluation=schemas.EvaluationResult(
            technical_score=evaluation["technical_score"],
            depth_score=evaluation["depth_score"],
            clarity_score=evaluation["clarity_score"],
            relevance_score=evaluation["relevance_score"],
            structure_score=evaluation["structure_score"],
            overall_score=overall_score,
            strengths=evaluation["strengths"],
            weaknesses=evaluation["weaknesses"],
            improvement_suggestions=evaluation["improvement_suggestions"]
        ),
        next_question=schemas.QuestionOut.from_orm(next_question) if next_question else None,
        is_last_question=is_last,
        questions_answered=answered_count,
        total_questions=session.question_count
    )


@router.get("/summary/{session_id}", response_model=schemas.SessionSummaryResponse)
def get_summary(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    import uuid
    summary = interview_service.get_session_summary(
        db=db,
        session_id=uuid.UUID(session_id),
        user_id=current_user.id
    )
    return schemas.SessionSummaryResponse(**summary)


@router.get("/history", response_model=schemas.SessionHistoryResponse)
def get_history(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    offset = (page - 1) * limit
    total = db.query(models.InterviewSession).filter(
        models.InterviewSession.user_id == current_user.id
    ).count()

    sessions = db.query(models.InterviewSession).filter(
        models.InterviewSession.user_id == current_user.id
    ).order_by(
        models.InterviewSession.created_at.desc()
    ).offset(offset).limit(limit).all()

    items = []
    for s in sessions:
        items.append(schemas.SessionListItem(
            id=s.id,
            role=s.role,
            level=s.level,
            interview_type=s.interview_type,
            difficulty=s.difficulty,
            question_count=s.question_count,
            total_score=s.total_score,
            status=s.status,
            rating=get_rating_from_score(s.total_score),
            created_at=s.created_at
        ))

    return schemas.SessionHistoryResponse(
        sessions=items,
        total=total,
        page=page,
        limit=limit,
        total_pages=math.ceil(total / limit)
    )


@router.get("/session/{session_id}", response_model=schemas.SessionDetailResponse)
def get_session_detail(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    import uuid
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.id == uuid.UUID(session_id),
        models.InterviewSession.user_id == current_user.id
    ).first()

    from fastapi import HTTPException, status
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    return schemas.SessionDetailResponse(
        id=session.id,
        role=session.role,
        level=session.level,
        interview_type=session.interview_type,
        difficulty=session.difficulty,
        question_count=session.question_count,
        total_score=session.total_score,
        status=session.status,
        timer_enabled=session.timer_enabled,
        time_per_question=session.time_per_question,
        questions=[schemas.QuestionSummary.from_orm(q) for q in session.questions],
        created_at=session.created_at,
        completed_at=session.completed_at
    )
@router.get("/session/{session_id}/resume", response_model=schemas.ResumeSessionResponse)
def resume_interview(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    import uuid
    session, current_question, answered_count = interview_service.resume_session(
        db=db,
        session_id=uuid.UUID(session_id),
        user_id=current_user.id
    )
    return schemas.ResumeSessionResponse(
        session_id=session.id,
        role=session.role,
        level=session.level,
        interview_type=session.interview_type,
        difficulty=session.difficulty,
        current_question=schemas.QuestionOut.from_orm(current_question),
        questions_answered=answered_count,
        total_questions=session.question_count,
        timer_enabled=session.timer_enabled,
        time_per_question=session.time_per_question
    )


@router.patch("/session/{session_id}/abandon", response_model=schemas.AbandonSessionResponse)
def abandon_interview(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    import uuid
    session = interview_service.abandon_session(
        db=db,
        session_id=uuid.UUID(session_id),
        user_id=current_user.id
    )
    return schemas.AbandonSessionResponse(session_id=session.id)
@router.get("/stats", response_model=schemas.InterviewStatsResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    stats = interview_service.get_interview_stats(
        db=db,
        user_id=current_user.id
    )
    return schemas.InterviewStatsResponse(**stats)
    