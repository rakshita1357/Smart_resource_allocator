from fastapi import APIRouter, HTTPException
from typing import List
from app.db.session import db
from app.models.volunteer import Volunteer

router = APIRouter(prefix="/volunteers", tags=["Volunteers"])


@router.post("/")
async def create_volunteer(payload: Volunteer):
    collection = db["volunteers"]

    # check duplicate email
    existing = await collection.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    result = await collection.insert_one(payload.dict(exclude={"id"}))

    return {"id": str(result.inserted_id)}


@router.get("/")
async def get_volunteers():
    collection = db["volunteers"]

    volunteers = []
    async for doc in collection.find():
        doc["_id"] = str(doc["_id"])
        volunteers.append(doc)

    return volunteers
# in process