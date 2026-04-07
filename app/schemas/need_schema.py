from pydantic import BaseModel
from typing import List, Optional


class NeedCreate(BaseModel):
    survey_id: int
    location: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    skills_required: Optional[List[str]] = []
    urgency_level: Optional[str]
    people_affected: Optional[int]


class NeedRead(BaseModel):
    id: int
    survey_id: int
    location: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    skills_required: Optional[List[str]] = []
    urgency_level: Optional[str]
    people_affected: Optional[int]

    class Config:
        orm_mode = True

