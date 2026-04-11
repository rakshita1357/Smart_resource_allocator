from pydantic import BaseModel
from typing import List, Optional

class Need(BaseModel):
    id: Optional[str] = None
    survey_id: str   # just store ID
    location: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    skills_required: Optional[List[str]] = []
    urgency_level: Optional[str]
    people_affected: Optional[int]