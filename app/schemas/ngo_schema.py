"""
Pydantic schemas for NGO create/read operations.
"""
from pydantic import BaseModel, EmailStr


class NGOCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    location: str


class NGORead(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    location: str

    # Pydantic v2-style config to allow constructing from ORM objects
    model_config = {"from_attributes": True}
