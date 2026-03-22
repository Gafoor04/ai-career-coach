from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.utils.auth import get_current_user
from app.services import profile_service

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/", response_model=schemas.ProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    profile = profile_service.get_or_create_profile(db, current_user.id)
    return schemas.ProfileResponse(**profile_service.serialize_profile(profile))


@router.put("/", response_model=schemas.ProfileResponse)
def update_profile(
    data: schemas.ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    profile = profile_service.update_profile(db, current_user.id, data)
    return schemas.ProfileResponse(**profile_service.serialize_profile(profile))