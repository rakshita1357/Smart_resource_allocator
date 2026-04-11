from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.ngo import NGO
from app.schemas.ngo_schema import NGOCreate, NGORead

router = APIRouter(prefix="/ngo", tags=["NGO"])


@router.post("/register", response_model=NGORead)
def register_ngo(payload: NGOCreate, db: Session = Depends(get_db)):
    """Register a new NGO and persist to the database."""
    existing = db.query(NGO).filter(NGO.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="NGO with this email already exists")

    ngo = NGO(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        location=payload.location,
    )
    db.add(ngo)
    db.commit()
    db.refresh(ngo)
    return ngo


@router.post("/create-drive")
def create_drive(payload: dict):
    """Minimal in-memory drive creation kept for compatibility."""
    # Lightweight in-memory drive store for demo; in production this should be a DB model
    drive = payload
    drive["id"] = 1
    return drive


@router.get("/drives")
def list_drives():
    """Return demo drives (empty for now)."""
    return []
