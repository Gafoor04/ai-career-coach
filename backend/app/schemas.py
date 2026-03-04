from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models import ExperienceLevel, InterviewType, Difficulty, SessionStatus


# ─── AUTH SCHEMAS ────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


# ─── INTERVIEW SETUP SCHEMAS ──────────────────────────────────────────────────

class InterviewStartRequest(BaseModel):
    role: str = Field(..., min_length=1, max_length=255, description="Job role e.g. Backend Developer")
    level: ExperienceLevel
    interview_type: InterviewType
    difficulty: Difficulty
    question_count: int = Field(..., ge=1, le=15)
    timer_enabled: bool = False
    time_per_question: Optional[int] = Field(None, ge=30, le=300)

    @validator("time_per_question", always=True)
    def validate_timer(cls, v, values):
        if values.get("timer_enabled") and v is None:
            raise ValueError("time_per_question is required when timer_enabled is True")
        return v


class QuestionOut(BaseModel):
    id: UUID
    question_index: int
    question_text: str
    category: Optional[str]

    class Config:
        from_attributes = True


class InterviewStartResponse(BaseModel):
    session_id: UUID
    first_question: QuestionOut
    total_questions: int
    message: str = "Interview session started successfully"


# ─── ANSWER SUBMISSION SCHEMAS ────────────────────────────────────────────────

class AnswerSubmitRequest(BaseModel):
    session_id: UUID
    question_id: UUID
    answer: str = Field(..., min_length=1, max_length=5000)


class EvaluationResult(BaseModel):
    technical_score: float = Field(..., ge=0, le=10)
    depth_score: float = Field(..., ge=0, le=10)
    clarity_score: float = Field(..., ge=0, le=10)
    relevance_score: float = Field(..., ge=0, le=10)
    structure_score: float = Field(..., ge=0, le=10)
    overall_score: float = Field(..., ge=0, le=10)
    strengths: str
    weaknesses: str
    improvement_suggestions: str


class AnswerSubmitResponse(BaseModel):
    evaluation: EvaluationResult
    next_question: Optional[QuestionOut]
    is_last_question: bool
    questions_answered: int
    total_questions: int


# ─── SESSION SUMMARY SCHEMAS ──────────────────────────────────────────────────

class QuestionSummary(BaseModel):
    id: UUID
    question_index: int
    question_text: str
    category: Optional[str]
    user_answer: Optional[str]
    technical_score: Optional[float]
    depth_score: Optional[float]
    clarity_score: Optional[float]
    relevance_score: Optional[float]
    structure_score: Optional[float]
    overall_score: Optional[float]
    strengths: Optional[str]
    weaknesses: Optional[str]
    improvement_suggestions: Optional[str]

    class Config:
        from_attributes = True


class AxisAverages(BaseModel):
    technical: float
    depth: float
    clarity: float
    relevance: float
    structure: float


class SessionSummaryResponse(BaseModel):
    session_id: UUID
    role: str
    level: str
    interview_type: str
    difficulty: str
    total_score: float
    rating: str
    rating_label: str
    axis_averages: AxisAverages
    questions: List[QuestionSummary]
    weak_areas: List[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ─── SESSION LIST SCHEMAS ─────────────────────────────────────────────────────

class SessionListItem(BaseModel):
    id: UUID
    role: str
    level: str
    interview_type: str
    difficulty: str
    question_count: int
    total_score: Optional[float]
    status: str
    rating: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SessionHistoryResponse(BaseModel):
    sessions: List[SessionListItem]
    total: int
    page: int
    limit: int
    total_pages: int


# ─── SESSION DETAIL ───────────────────────────────────────────────────────────

class SessionDetailResponse(BaseModel):
    id: UUID
    role: str
    level: str
    interview_type: str
    difficulty: str
    question_count: int
    total_score: Optional[float]
    status: str
    timer_enabled: bool
    time_per_question: Optional[int]
    questions: List[QuestionSummary]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True