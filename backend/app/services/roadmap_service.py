import uuid
import json
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import models, schemas
from app.services import llm_service


def generate_roadmap(
    db: Session,
    user_id: uuid.UUID,
    target_role: str,
    experience_level: str,
    current_skills: list
) -> models.Roadmap:
    """Generate roadmap via LLM and save to DB."""

    roadmap_data = llm_service.generate_roadmap(
        target_role=target_role,
        experience_level=experience_level,
        current_skills=current_skills
    )

    roadmap = models.Roadmap(
        user_id=user_id,
        target_role=target_role,
        current_skills=",".join(current_skills) if current_skills else None,
        experience_level=experience_level,
        roadmap_data=json.dumps(roadmap_data)
    )

    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)
    return roadmap


def get_roadmap(
    db: Session,
    roadmap_id: uuid.UUID,
    user_id: uuid.UUID
) -> models.Roadmap:
    roadmap = db.query(models.Roadmap).filter(
        models.Roadmap.id == roadmap_id,
        models.Roadmap.user_id == user_id
    ).first()

    if not roadmap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")

    return roadmap


def get_user_roadmaps(
    db: Session,
    user_id: uuid.UUID
) -> list:
    return db.query(models.Roadmap).filter(
        models.Roadmap.user_id == user_id
    ).order_by(models.Roadmap.created_at.desc()).all()


def delete_roadmap(
    db: Session,
    roadmap_id: uuid.UUID,
    user_id: uuid.UUID
):
    roadmap = get_roadmap(db, roadmap_id, user_id)
    db.delete(roadmap)
    db.commit()