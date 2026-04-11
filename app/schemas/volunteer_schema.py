"""
Improved Volunteer Pydantic schemas with Pydantic v2 compatibility and explicit typing.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


class VolunteerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    skills: List[str] = Field(default_factory=list)
    availability: Optional[str] = None
    experience_level: Optional[str] = None

    # Pydantic v2-compatible config to allow constructing from ORM objects
    model_config = {"from_attributes": True}


class VolunteerRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    skills: List[str] = Field(default_factory=list)
    availability: Optional[str] = None
    experience_level: Optional[str] = None

    model_config = {"from_attributes": True}
