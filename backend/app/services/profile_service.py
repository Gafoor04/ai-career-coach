import uuid
import json
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import models, schemas


def compute_profile_strength(profile: models.UserProfile) -> float:
    """Score profile completeness out of 100."""
    score = 0.0

    if profile.bio: score += 15
    if profile.career_goal: score += 10
    if profile.target_role: score += 15
    if profile.location: score += 5
    if profile.phone: score += 5
    if profile.github_url: score += 15
    if profile.linkedin_url: score += 10
    if profile.leetcode_url: score += 5
    if profile.portfolio_url: score += 5
    if profile.skills:
        skills = [s.strip() for s in profile.skills.split(",") if s.strip()]
        if len(skills) >= 5:
            score += 10
        elif len(skills) >= 1:
            score += 5
    if profile.certifications:
        score += 5

    return round(min(score, 100.0), 1)


def get_or_create_profile(
    db: Session,
    user_id: uuid.UUID
) -> models.UserProfile:
    """Get existing profile or create empty one."""
    profile = db.query(models.UserProfile).filter(
        models.UserProfile.user_id == user_id
    ).first()

    if not profile:
        profile = models.UserProfile(user_id=user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return profile


def update_profile(
    db: Session,
    user_id: uuid.UUID,
    data: schemas.ProfileUpdateRequest
) -> models.UserProfile:
    """Update profile fields."""
    profile = get_or_create_profile(db, user_id)

    if data.bio is not None:
        profile.bio = data.bio
    if data.career_goal is not None:
        profile.career_goal = data.career_goal
    if data.target_role is not None:
        profile.target_role = data.target_role
    if data.location is not None:
        profile.location = data.location
    if data.phone is not None:
        profile.phone = data.phone
    if data.github_url is not None:
        profile.github_url = data.github_url
    if data.linkedin_url is not None:
        profile.linkedin_url = data.linkedin_url
    if data.leetcode_url is not None:
        profile.leetcode_url = data.leetcode_url
    if data.codechef_url is not None:
        profile.codechef_url = data.codechef_url
    if data.portfolio_url is not None:
        profile.portfolio_url = data.portfolio_url
    if data.skills is not None:
        profile.skills = ",".join(data.skills)
    if data.certifications is not None:
        profile.certifications = json.dumps(
            [c.dict() for c in data.certifications]
        )

    profile.profile_strength = compute_profile_strength(profile)
    profile.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(profile)
    return profile


def serialize_profile(profile: models.UserProfile) -> dict:
    """Convert DB model to response dict, deserializing JSON fields."""
    skills = []
    if profile.skills:
        skills = [s.strip() for s in profile.skills.split(",") if s.strip()]

    certifications = []
    if profile.certifications:
        try:
            certifications = json.loads(profile.certifications)
        except Exception:
            certifications = []

    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "bio": profile.bio,
        "career_goal": profile.career_goal,
        "target_role": profile.target_role,
        "location": profile.location,
        "phone": profile.phone,
        "github_url": profile.github_url,
        "linkedin_url": profile.linkedin_url,
        "leetcode_url": profile.leetcode_url,
        "codechef_url": profile.codechef_url,
        "portfolio_url": profile.portfolio_url,
        "skills": skills,
        "certifications": certifications,
        "profile_strength": profile.profile_strength,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at,
    }