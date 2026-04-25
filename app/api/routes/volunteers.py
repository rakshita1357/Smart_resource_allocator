from typing import Any

from fastapi import APIRouter, Depends

from app.db.mongodb import get_db

router = APIRouter(prefix="/volunteers", tags=["Volunteers"])


@router.get("/")
async def get_volunteers(db: Any = Depends(get_db)):
    """Return a list of volunteers from MongoDB."""
    volunteers = await db.volunteers.find().to_list(length=100)
    for volunteer in volunteers:
        volunteer["_id"] = str(volunteer["_id"])
    return volunteers
