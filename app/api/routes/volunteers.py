from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.db.mongodb import get_db
from app.schemas.volunteer_schema import VolunteerCreate, VolunteerRead

router = APIRouter(prefix="/volunteer", tags=["Volunteer"])


@router.post("/register", response_model=VolunteerRead, status_code=status.HTTP_201_CREATED)
async def register_volunteer(payload: VolunteerCreate, db=Depends(get_db)):
    """Register a new volunteer using MongoDB."""
    existing = await db.volunteers.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="Volunteer with this email already exists")

    payload_dict = payload.model_dump()
    result = await db.volunteers.insert_one(payload_dict)
    inserted_id = str(result.inserted_id)
    # Return the created resource with string id
    response = {"id": inserted_id, **payload_dict}
    return response


@router.get("/", response_model=List[VolunteerRead])
async def list_volunteers(db=Depends(get_db)):
    """List all volunteers."""
    docs = await db.volunteers.find().to_list(length=100)
    response = []
    for d in docs:
        d_id = str(d.get("_id") or d.get("id"))
        # build dict without '_id'
        item = {"id": d_id, **{k: v for k, v in d.items() if k != "_id"}}
        response.append(item)
    return response
