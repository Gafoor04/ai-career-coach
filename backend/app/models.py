import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean,
    DateTime, Text, ForeignKey, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class ExperienceLevel(str, enum.Enum):
    fresher = "fresher"
    mid = "mid"
    senior = "senior"


class InterviewType(str, enum.Enum):
    technical = "technical"
    hr = "hr"
    behavioral = "behavioral"
    system_design = "system_design"


class Difficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class SessionStatus(str, enum.Enum):
    in_progress = "in_progress"
    completed = "completed"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    sessions = relationship("InterviewSession", back_populates="user", cascade="all, delete-orphan")


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(255), nullable=False)
    level = Column(SAEnum(ExperienceLevel), nullable=False)
    interview_type = Column(SAEnum(InterviewType), nullable=False)
    difficulty = Column(SAEnum(Difficulty), nullable=False)
    question_count = Column(Integer, nullable=False)
    total_score = Column(Float, nullable=True)
    status = Column(SAEnum(SessionStatus), default=SessionStatus.in_progress, nullable=False)
    timer_enabled = Column(Boolean, default=False)
    time_per_question = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="sessions")
    questions = relationship(
        "InterviewQuestion",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="InterviewQuestion.question_index"
    )


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    question_index = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    category = Column(String(255), nullable=True)
    user_answer = Column(Text, nullable=True)
    technical_score = Column(Float, nullable=True)
    depth_score = Column(Float, nullable=True)
    clarity_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    structure_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True)
    strengths = Column(Text, nullable=True)
    weaknesses = Column(Text, nullable=True)
    improvement_suggestions = Column(Text, nullable=True)
    answered_at = Column(DateTime, nullable=True)

    session = relationship("InterviewSession", back_populates="questions")