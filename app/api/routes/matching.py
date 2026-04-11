from fastapi import APIRouter, HTTPException
from app.services.matching_engine import match_volunteers

router = APIRouter(prefix="/match", tags=["Matching"])


@router.get("/need/{need_id}")
async def get_matches(need_id: str):
    matches = await match_volunteers(need_id)

    if not matches:
        raise HTTPException(status_code=404, detail="No matches found")

    return {
        "need_id": need_id,
        "matches": matches
    }