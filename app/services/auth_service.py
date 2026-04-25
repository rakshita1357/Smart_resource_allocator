from __future__ import annotations

from datetime import datetime, timedelta, timezone
from importlib import import_module
from typing import Any
import secrets

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
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
    VolunteerRegisterResponse,
)

USER_COLLECTIONS: dict[str, str] = {"volunteer": "volunteers", "ngo": "ngos"}
OTP_COLLECTION = "otp_codes"


def _google_modules() -> tuple[Any, Any]:
    """Load Google auth modules lazily so startup stays resilient."""
    try:
        google_id_token = import_module("google.oauth2.id_token")
        google_requests = import_module("google.auth.transport.requests")
    except ModuleNotFoundError as exc:  # pragma: no cover - dependency guard
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google login dependencies are not installed",
        ) from exc
    return google_id_token, google_requests


async def ensure_auth_indexes(db: Any) -> None:
    """Create MongoDB indexes required by the auth module."""
    await db["volunteers"].create_index("email", unique=True)
    await db["ngos"].create_index("email", unique=True)
    await db["volunteers"].create_index("google_sub", unique=True, sparse=True)
    await db[OTP_COLLECTION].create_index("email", unique=True)
    await db[OTP_COLLECTION].create_index("expires_at")


async def _find_user_by_email(
    db: Any, email: str
) -> tuple[str | None, str | None, dict[str, Any] | None]:
    """Return the role, collection name, and document for the matching user email."""
    for role, collection_name in USER_COLLECTIONS.items():
        document = await db[collection_name].find_one({"email": email})
        if document:
            return role, collection_name, document
    return None, None, None


async def _email_exists(db: Any, email: str) -> bool:
    """Check whether an email already exists in either user collection."""
    role, _, _ = await _find_user_by_email(db, email)
    return role is not None



def _public_volunteer_response(document: dict[str, Any], inserted_id: str) -> VolunteerRegisterResponse:
    """Build a volunteer response payload without password fields."""
    return VolunteerRegisterResponse(
        id=inserted_id,
        role="volunteer",
        name=document["name"],
        email=document["email"],
        phone=document["phone"],
        latitude=document["latitude"],
        longitude=document["longitude"],
        skills=document.get("skills", []),
        availability=document["availability"],
        experience_level=document["experience_level"],
    )


def _public_ngo_response(document: dict[str, Any], inserted_id: str) -> NGORegisterResponse:
    """Build an NGO response payload without password fields."""
    return NGORegisterResponse(
        id=inserted_id,
        role="ngo",
        name=document["name"],
        email=document["email"],
        phone=document["phone"],
        location=document["location"],
    )


async def register_volunteer(
    db: Any, payload: VolunteerRegister
) -> VolunteerRegisterResponse:
    """Register a volunteer in MongoDB."""
    if await _email_exists(db, payload.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    document = payload.model_dump(exclude={"password"})
    document.update(
        {
            "role": "volunteer",
            "hashed_password": hash_password(payload.password),
            "created_at": datetime.now(timezone.utc),
        }
    )

    result = await db[USER_COLLECTIONS["volunteer"]].insert_one(document)
    return _public_volunteer_response(document, str(result.inserted_id))


async def register_ngo(db: Any, payload: NGORegister) -> NGORegisterResponse:
    """Register an NGO in MongoDB."""
    if await _email_exists(db, payload.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    document = payload.model_dump(exclude={"password"})
    document.update(
        {
            "role": "ngo",
            "hashed_password": hash_password(payload.password),
            "created_at": datetime.now(timezone.utc),
        }
    )

    result = await db[USER_COLLECTIONS["ngo"]].insert_one(document)
    return _public_ngo_response(document, str(result.inserted_id))


async def login_user(db: Any, payload: LoginRequest) -> TokenResponse:
    """Authenticate a volunteer or NGO and return a JWT access token."""
    collection_name = USER_COLLECTIONS[payload.role]
    user = await db[collection_name].find_one({"email": payload.email})

    if not user or not user.get("hashed_password"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    try:
        is_valid = verify_password(payload.password, user["hashed_password"])
    except Exception as exc:  # pragma: no cover - defensive guard for malformed hashes
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Password verification failed") from exc

    if not is_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token({"sub": payload.email, "role": payload.role})
    return TokenResponse(access_token=token)


async def forgot_password(db: Any, payload: ForgotPasswordRequest) -> MessageResponse:
    """Generate and store a one-time passcode for password reset."""
    role, _, user = await _find_user_by_email(db, payload.email)
    if not user or not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    otp = f"{secrets.randbelow(1_000_000):06d}"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)

    await db[OTP_COLLECTION].replace_one(
        {"email": payload.email},
        {
            "email": payload.email,
            "role": role,
            "otp": otp,
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc),
        },
        upsert=True,
    )

    await _send_otp_email(payload.email, otp)
    return MessageResponse(message="OTP generated and sent successfully")


async def reset_password(db: Any, payload: ResetPasswordRequest) -> MessageResponse:
    """Validate an OTP and update the user's password."""
    otp_document = await db[OTP_COLLECTION].find_one({"email": payload.email})
    if not otp_document:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")

    expires_at = otp_document.get("expires_at")
    if not isinstance(expires_at, datetime) or expires_at < datetime.now(timezone.utc):
        await db[OTP_COLLECTION].delete_one({"email": payload.email})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")

    if otp_document.get("otp") != payload.otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

    role = otp_document.get("role")
    if role not in USER_COLLECTIONS:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="OTP record is missing role metadata")

    collection_name = USER_COLLECTIONS[role]
    user = await db[collection_name].find_one({"email": payload.email})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await db[collection_name].update_one(
        {"email": payload.email},
        {
            "$set": {
                "hashed_password": hash_password(payload.new_password),
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )
    await db[OTP_COLLECTION].delete_one({"email": payload.email})

    return MessageResponse(message="Password reset successfully")


async def google_login(db: Any, payload: GoogleLoginRequest) -> TokenResponse:
    """Authenticate with Google OAuth and create a volunteer account on first login."""
    google_id_token, google_requests = _google_modules()
    audience = settings.GOOGLE_CLIENT_ID or None
    try:
        token_info = google_id_token.verify_oauth2_token(
            payload.token,
            google_requests.Request(),
            audience=audience,
        )
    except Exception as exc:  # pragma: no cover - external token verification
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token") from exc

    email = token_info.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google token did not include an email address")

    if token_info.get("email_verified") is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google email is not verified")

    name = token_info.get("name") or email.split("@")[0]
    google_sub = token_info.get("sub")

    role, collection_name, user = await _find_user_by_email(db, email)
    if not user:
        role = "volunteer"
        collection_name = USER_COLLECTIONS[role]
        document = {
            "role": role,
            "email": email,
            "hashed_password": "",
            "name": name,
            "phone": "",
            "latitude": 0.0,
            "longitude": 0.0,
            "skills": [],
            "availability": "anytime",
            "experience_level": "beginner",
            "google_sub": google_sub,
            "auth_provider": "google",
            "created_at": datetime.now(timezone.utc),
        }
        await db[collection_name].insert_one(document)
    elif role is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to determine account role")

    token = create_access_token({"sub": email, "role": role})
    return TokenResponse(access_token=token)


async def _send_otp_email(email: str, otp: str) -> None:
    """Placeholder for email delivery integration."""
    # Replace this with a real email provider in production.
    _ = email
    _ = otp

