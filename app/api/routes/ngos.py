from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from app.db.session import db

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


@router.post("/register")
async def register_ngo(payload: NGORegister):
    collection = db["ngos"]

    existing = await collection.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="NGO already exists")

    result = await collection.insert_one(payload.dict())

    return {"id": str(result.inserted_id)}


@router.post("/create-drive")
async def create_drive(payload: DriveCreate):
    collection = db["drives"]

    result = await collection.insert_one(payload.dict())

    return {"id": str(result.inserted_id)}


@router.get("/drives")
async def list_drives():
    collection = db["drives"]

    drives = []
    async for doc in collection.find():
        doc["_id"] = str(doc["_id"])
        drives.append(doc)

    return drives

# in process