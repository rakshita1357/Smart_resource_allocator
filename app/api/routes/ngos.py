from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.db.session import get_db
from app.models import survey, volunteer  # noqa: F401

router = APIRouter(prefix="/ngo", tags=["NGO"])


class NGORegister(BaseModel):
    name: str
    email: str
    phone: str
    location: str


class DriveCreate(BaseModel):
    title: str
    description: str
    location: str
    urgency_level: str
    skills_required: List[str]
    volunteers_needed: int


# For minimal implementation we'll store NGOs and drives in memory
NGOS = []
DRIVES = []


@router.post("/register")
def register_ngo(payload: NGORegister):
    """Register a new NGO (in-memory for minimal demo)."""
    for n in NGOS:
        if n["email"] == payload.email:
            raise HTTPException(status_code=400, detail="NGO with this email already exists")
    ngo = payload.dict()
    ngo["id"] = len(NGOS) + 1
    NGOS.append(ngo)
    return ngo


@router.post("/create-drive")
def create_drive(payload: DriveCreate):
    """Create a drive linked to an NGO (minimal in-memory implementation)."""
    drive = payload.dict()
    drive["id"] = len(DRIVES) + 1
    DRIVES.append(drive)
    return drive


@router.get("/drives")
def list_drives():
    return DRIVES

