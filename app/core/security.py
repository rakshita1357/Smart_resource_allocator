from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
import base64
import hashlib
import hmac
import json

from app.core.config import settings

try:
    from jose import jwt as jose_jwt
except ModuleNotFoundError:  # pragma: no cover - optional dependency guard
    jose_jwt = None

try:
    from passlib.context import CryptContext
except ModuleNotFoundError:  # pragma: no cover - optional dependency guard
    CryptContext = None

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str):
    """Hash a plain text password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    """Verify a plain text password against a bcrypt hash."""
    return pwd_context.verify(password, hashed_password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT token."""
    payload = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({"exp": int(expire.timestamp())})

    if jose_jwt is not None:
        return jose_jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _urlsafe_b64(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _urlsafe_b64(json.dumps(payload, default=str, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(settings.SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    signature_b64 = _urlsafe_b64(signature)
    return f"{header_b64}.{payload_b64}.{signature_b64}"


def _urlsafe_b64(value: bytes) -> str:
    """Encode bytes using URL-safe base64 without padding."""
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("utf-8")
