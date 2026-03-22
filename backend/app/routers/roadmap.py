import uuid
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.utils.auth import get_current_user
from app.services import roadmap_service
from typing import List

router = APIRouter(prefix="/roadmap", tags=["Roadmap"])


@router.post("/generate", response_model=schemas.RoadmapResponse)
def generate_roadmap(
    request: schemas.RoadmapGenerateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    roadmap = roadmap_service.generate_roadmap(
        db=db,
        user_id=current_user.id,
        target_role=request.target_role,
        experience_level=request.experience_level,
        current_skills=request.current_skills or []
    )
    return schemas.RoadmapResponse(
        id=roadmap.id,
        target_role=roadmap.target_role,
        experience_level=roadmap.experience_level,
        roadmap_data=json.loads(roadmap.roadmap_data),
        created_at=roadmap.created_at
    )


@router.get("/", response_model=List[schemas.RoadmapListItem])
def get_roadmaps(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return roadmap_service.get_user_roadmaps(db, current_user.id)


@router.get("/{roadmap_id}", response_model=schemas.RoadmapResponse)
def get_roadmap(
    roadmap_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    roadmap = roadmap_service.get_roadmap(db, uuid.UUID(roadmap_id), current_user.id)
    return schemas.RoadmapResponse(
        id=roadmap.id,
        target_role=roadmap.target_role,
        experience_level=roadmap.experience_level,
        roadmap_data=json.loads(roadmap.roadmap_data),
        created_at=roadmap.created_at
    )


@router.delete("/{roadmap_id}")
def delete_roadmap(
    roadmap_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    roadmap_service.delete_roadmap(db, uuid.UUID(roadmap_id), current_user.id)
    return {"message": "Roadmap deleted successfully"}