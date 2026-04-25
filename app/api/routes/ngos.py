from typing import List

from pydantic import BaseModel
from fastapi import APIRouter

from app.db.session import db

router = APIRouter(prefix="/ngo", tags=["NGO"])


class DriveCreate(BaseModel):
    title: str
    description: str
    location: str
    urgency_level: str
    skills_required: List[str]
    volunteers_needed: int


@router.post("/create-drive")
async def create_drive(payload: DriveCreate):
    collection = db["drives"]

    result = await collection.insert_one(payload.model_dump())

    return {"id": str(result.inserted_id)}


@router.get("/drives")
async def list_drives():
    collection = db["drives"]

    drives = []
    async for doc in collection.find():
        doc["_id"] = str(doc["_id"])
        drives.append(doc)

    return drives
