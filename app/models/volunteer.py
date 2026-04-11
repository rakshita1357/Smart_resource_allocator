from pydantic import BaseModel, EmailStr
from typing import List, Optional

class Volunteer(BaseModel):
    id: Optional[str] = None
    name: str
    email: EmailStr
    phone: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    skills: Optional[List[str]] = []
    availability: Optional[str]
    experience_level: Optional[str]

    # in process