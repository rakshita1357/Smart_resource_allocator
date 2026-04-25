from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import hash_password
from app.db.mongodb import get_db
from app.schemas.auth_schema import (
    ForgotPasswordRequest,
    GoogleLoginRequest,
    LoginRequest,
    MessageResponse,
    NGORegister,
    NGORegisterResponse,
    ResetPasswordRequest,
    TokenResponse,
    VolunteerRegister,
    VolunteerRegistrationResponse,
)
from app.services.auth_service import (
    forgot_password,
    google_login,
    login_user,
    register_ngo,
    reset_password,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register/volunteer",
    response_model=VolunteerRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_volunteer_endpoint(
    payload: VolunteerRegister,
    db: Any = Depends(get_db),
) -> VolunteerRegistrationResponse:
    """Register a volunteer account in MongoDB Atlas."""
    try:
        print(type(payload.password))
        print(payload.password)

        if len(payload.password.encode("utf-8")) > 72:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password too long. Max 72 bytes.",
            )

        existing = await db.volunteers.find_one({"email": payload.email})
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Volunteer already exists")

        volunteer_doc = {
            "role": "volunteer",
            "name": payload.name,
            "email": payload.email,
            "phone": payload.phone,
            "latitude": payload.latitude,
            "longitude": payload.longitude,
            "skills": payload.skills,
            "availability": payload.availability,
            "experience_level": payload.experience_level,
            "hashed_password": hash_password(payload.password),
        }

        result = await db.volunteers.insert_one(volunteer_doc)
        return VolunteerRegistrationResponse(
            id=str(result.inserted_id),
            message="Volunteer registered successfully",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.post(
    "/register/ngo",
    response_model=NGORegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_ngo_endpoint(
    payload: NGORegister,
    db: Any = Depends(get_db),
) -> NGORegisterResponse:
    """Register an NGO account."""
    return await register_ngo(db, payload)


@router.post("/login", response_model=TokenResponse)
async def login_endpoint(
    payload: LoginRequest,
    db: Any = Depends(get_db),
) -> TokenResponse:
    """Authenticate a volunteer or NGO and issue a JWT token."""
    return await login_user(db, payload)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password_endpoint(
    payload: ForgotPasswordRequest,
    db: Any = Depends(get_db),
) -> MessageResponse:
    """Generate and store an OTP for password reset."""
    return await forgot_password(db, payload)


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password_endpoint(
    payload: ResetPasswordRequest,
    db: Any = Depends(get_db),
) -> MessageResponse:
    """Validate an OTP and update the user's password."""
    return await reset_password(db, payload)


@router.post("/google-login", response_model=TokenResponse)
async def google_login_endpoint(
    payload: GoogleLoginRequest,
    db: Any = Depends(get_db),
) -> TokenResponse:
    """Authenticate using a Google OAuth token."""
    return await google_login(db, payload)
