from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class VolunteerRegister(BaseModel):
    """Request payload for volunteer registration."""

    name: str
    email: EmailStr
    phone: str
    latitude: float
    longitude: float
    skills: list[str] = Field(default_factory=list)
    availability: str
    experience_level: str
    password: str

    class Config:
        from_attributes = True


class VolunteerRegistrationResponse(BaseModel):
    """Response payload for volunteer registration."""

    id: str
    message: str

    class Config:
        from_attributes = True


class VolunteerRegisterResponse(BaseModel):
    """Legacy response payload kept for compatibility with existing service code."""

    id: str
    role: Literal["volunteer"]
    name: str
    email: EmailStr
    phone: str
    latitude: float
    longitude: float
    skills: list[str] = Field(default_factory=list)
    availability: str
    experience_level: str

    class Config:
        from_attributes = True


class NGORegister(BaseModel):
    """Request payload for NGO registration."""

    name: str
    email: EmailStr
    phone: str
    location: str
    password: str

    class Config:
        from_attributes = True


class NGORegisterResponse(BaseModel):
    """Response payload for NGO registration."""

    id: str
    role: Literal["ngo"]
    name: str
    email: EmailStr
    phone: str
    location: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Request payload for role-based login."""

    role: Literal["volunteer", "ngo"]
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


class ForgotPasswordRequest(BaseModel):
    """Request payload for OTP generation."""

    email: EmailStr

    class Config:
        from_attributes = True


class ResetPasswordRequest(BaseModel):
    """Request payload for OTP-based password reset."""

    email: EmailStr
    otp: str
    new_password: str

    class Config:
        from_attributes = True


class GoogleLoginRequest(BaseModel):
    """Request payload for Google sign-in."""

    token: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response payload."""

    access_token: str
    token_type: str = "bearer"

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Generic message response payload."""

    message: str

    class Config:
        from_attributes = True
