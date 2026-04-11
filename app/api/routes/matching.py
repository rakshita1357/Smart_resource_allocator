from fastapi import APIRouter, Depends, HTTPException
from app.db.mongodb import get_db
from app.services.matching_engine import match_volunteers

router = APIRouter(prefix="/match", tags=["Matching"])


@router.get("/need/{need_id}")
async def get_matches(need_id: str, db=Depends(get_db)):
    """Return top matched volunteers for a need id."""
    matches = await match_volunteers(db, need_id)
    if matches is None:
        raise HTTPException(status_code=404, detail="Need not found or no matches")
    return {"need_id": need_id, "matches": matches}
