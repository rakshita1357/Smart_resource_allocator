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
    id: str
    name: str
    email: EmailStr
    phone: str
    location: str

    model_config = {"from_attributes": True}
