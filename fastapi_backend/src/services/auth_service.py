from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.errors import AppError
from src.core.security import create_access_token, create_refresh_token, decode_token, verify_password
from src.models.user import User


class AuthService:
    """Authentication use-cases (login and refresh)."""

    def __init__(self, db: Session):
        self.db = db

    def login(self, email: str, password: str) -> tuple[str, str]:
        user = self.db.scalar(select(User).where(User.email == email))
        if not user or not user.is_active:
            raise AppError(status_code=401, code="invalid_credentials", message="Invalid email or password")
        if not verify_password(password, user.hashed_password):
            raise AppError(status_code=401, code="invalid_credentials", message="Invalid email or password")

        access = create_access_token(subject=str(user.id), role=user.role)
        refresh = create_refresh_token(subject=str(user.id))
        return access, refresh

    def refresh(self, refresh_token: str) -> tuple[str, str]:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise AppError(status_code=401, code="invalid_token", message="Refresh token required")
        user_id = payload.get("sub")
        if not user_id:
            raise AppError(status_code=401, code="invalid_token", message="Token subject missing")

        user = self.db.get(User, user_id)
        if not user or not user.is_active:
            raise AppError(status_code=401, code="inactive_user", message="User not found or inactive")

        access = create_access_token(subject=str(user.id), role=user.role)
        refresh = create_refresh_token(subject=str(user.id))
        return access, refresh
