from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.volunteer import Volunteer
from app.schemas.volunteer_schema import VolunteerCreate, VolunteerRead

router = APIRouter(prefix="/volunteer", tags=["Volunteer"])


@router.post("/register", response_model=VolunteerRead)
def register_volunteer(payload: VolunteerCreate, db: Session = Depends(get_db)):
    """Register a new volunteer and persist to the database."""
    existing = db.query(Volunteer).filter(Volunteer.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Volunteer with this email already exists")

    vol = Volunteer(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        latitude=payload.latitude,
        longitude=payload.longitude,
        skills=payload.skills or [],
        availability=payload.availability,
        experience_level=payload.experience_level,
    )
    db.add(vol)
    db.commit()
    db.refresh(vol)
    return vol


@router.get("/", response_model=List[VolunteerRead])
def list_volunteers(db: Session = Depends(get_db)):
    """List all registered volunteers."""
    vols = db.query(Volunteer).all()
    return vols
