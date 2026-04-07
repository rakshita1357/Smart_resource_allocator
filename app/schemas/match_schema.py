from pydantic import BaseModel
from typing import Any, Dict, List


class MatchResult(BaseModel):
    match_id: int
    volunteer: Dict[str, Any]
    score: float


class MatchListResponse(BaseModel):
    need_id: int
    matches: List[MatchResult]

