from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import uuid

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import settings
from src.core.errors import AppError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# PUBLIC_INTERFACE
def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


# PUBLIC_INTERFACE
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(subject: str, token_type: str, expires_delta: timedelta, extra: Optional[Dict[str, Any]] = None) -> str:
    now = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        "sub": subject,
        "type": token_type,  # "access" | "refresh"
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "jti": str(uuid.uuid4()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


# PUBLIC_INTERFACE
def create_access_token(subject: str, role: str) -> str:
    """Create a signed JWT access token for a user."""
    return _create_token(
        subject=subject,
        token_type="access",
        expires_delta=timedelta(minutes=settings.access_token_expires_minutes),
        extra={"role": role},
    )


# PUBLIC_INTERFACE
def create_refresh_token(subject: str) -> str:
    """Create a signed JWT refresh token for a user."""
    return _create_token(
        subject=subject,
        token_type="refresh",
        expires_delta=timedelta(minutes=settings.refresh_token_expires_minutes),
    )


# PUBLIC_INTERFACE
def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token; raises AppError on failure."""
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as e:
        raise AppError(status_code=401, code="invalid_token", message="Invalid or expired token") from e


# PUBLIC_INTERFACE
def split_bearer_token(authorization_header: Optional[str]) -> str:
    """Extract raw token from an Authorization: Bearer <token> header."""
    if not authorization_header:
        raise AppError(status_code=401, code="missing_auth", message="Missing Authorization header")
    parts = authorization_header.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AppError(status_code=401, code="invalid_auth", message="Authorization header must be Bearer token")
    return parts[1].strip()
