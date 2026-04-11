from typing import Optional
import hashlib


def hash_password(password: str) -> str:
    """Return a simple SHA256 hash of the password. Replace with a proper hashing in production."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

# in process