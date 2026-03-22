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
    is_followup: bool = False 

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
# ─── RESUME / ABANDON SCHEMAS ─────────────────────────────────────────────────

class ResumeSessionResponse(BaseModel):
    session_id: UUID
    role: str
    level: str
    interview_type: str
    difficulty: str
    current_question: QuestionOut
    questions_answered: int
    total_questions: int
    timer_enabled: bool
    time_per_question: Optional[int]

    class Config:
        from_attributes = True


class AbandonSessionResponse(BaseModel):
    session_id: UUID
    message: str = "Session abandoned successfully"
# ─── STATS SCHEMAS ────────────────────────────────────────────────────────────

class ScoreTrendItem(BaseModel):
    session_id: UUID
    role: str
    total_score: float
    created_at: datetime

class InterviewStatsResponse(BaseModel):
    total_interviews: int
    completed_interviews: int
    abandoned_interviews: int
    average_score: Optional[float]
    best_score: Optional[float]
    worst_score: Optional[float]
    most_practiced_role: Optional[str]
    score_trend: List[ScoreTrendItem]
    average_by_type: dict
    average_by_difficulty: dict
# ─── PROFILE SCHEMAS ──────────────────────────────────────────────────────────

class CertificationItem(BaseModel):
    name: str
    issuer: Optional[str] = None
    year: Optional[int] = None


class ProfileUpdateRequest(BaseModel):
    bio: Optional[str] = Field(None, max_length=1000)
    career_goal: Optional[str] = Field(None, max_length=500)
    target_role: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    github_url: Optional[str] = Field(None, max_length=500)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    leetcode_url: Optional[str] = Field(None, max_length=500)
    codechef_url: Optional[str] = Field(None, max_length=500)
    portfolio_url: Optional[str] = Field(None, max_length=500)
    skills: Optional[List[str]] = None
    certifications: Optional[List[CertificationItem]] = None


class ProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    bio: Optional[str]
    career_goal: Optional[str]
    target_role: Optional[str]
    location: Optional[str]
    phone: Optional[str]
    github_url: Optional[str]
    linkedin_url: Optional[str]
    leetcode_url: Optional[str]
    codechef_url: Optional[str]
    portfolio_url: Optional[str]
    skills: Optional[List[str]]
    certifications: Optional[List[CertificationItem]]
    profile_strength: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
# ─── ROADMAP SCHEMAS ───────────────────────────────────────────────────────────

class RoadmapGenerateRequest(BaseModel):
    target_role: str = Field(..., min_length=1, max_length=255)
    experience_level: ExperienceLevel
    current_skills: Optional[List[str]] = []


class RoadmapListItem(BaseModel):
    id: UUID
    target_role: str
    experience_level: str
    created_at: datetime

    class Config:
        from_attributes = True


class RoadmapResponse(BaseModel):
    id: UUID
    target_role: str
    experience_level: str
    roadmap_data: dict
    created_at: datetime

    class Config:
        from_attributes = True