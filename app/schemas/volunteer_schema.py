from pydantic import BaseModel, EmailStr
from typing import List, Optional


class VolunteerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    skills: Optional[List[str]] = []
    availability: Optional[str]
    experience_level: Optional[str]


class VolunteerRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    skills: Optional[List[str]] = []
    availability: Optional[str]
    experience_level: Optional[str]

    class Config:
        orm_mode = True

# in process