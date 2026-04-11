from fastapi import APIRouter, Depends, HTTPException, status
from app.db.mongodb import get_db
from app.schemas.ngo_schema import NGOCreate, NGORead

router = APIRouter(prefix="/ngo", tags=["NGO"])


@router.post("/register", response_model=NGORead, status_code=status.HTTP_201_CREATED)
async def register_ngo(payload: NGOCreate, db=Depends(get_db)):
    """Register a new NGO in MongoDB."""
    existing = await db.ngos.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="NGO with this email already exists")

    payload_dict = payload.model_dump()
    result = await db.ngos.insert_one(payload_dict)
    inserted_id = str(result.inserted_id)
    response = {"id": inserted_id, **payload_dict}
    return response


@router.post("/create-drive")
async def create_drive(payload: dict):
    """Minimal drive creation endpoint (stores in-memory for now)."""
    drive = payload
    drive["id"] = 1
    return drive


@router.get("/drives")
async def list_drives():
    return []
