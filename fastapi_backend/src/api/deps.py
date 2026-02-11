from __future__ import annotations

from typing import Annotated, Optional

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from src.core.errors import AppError
from src.core.security import decode_token, split_bearer_token
from src.db.session import get_db
from src.models.user import User


# PUBLIC_INTERFACE
def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    authorization: Annotated[Optional[str], Header()] = None,
) -> User:
    """Resolve current user from Bearer JWT access token."""
    token = split_bearer_token(authorization)
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise AppError(status_code=401, code="invalid_token", message="Access token required")
    user_id = payload.get("sub")
    if not user_id:
        raise AppError(status_code=401, code="invalid_token", message="Token subject missing")

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise AppError(status_code=401, code="inactive_user", message="User not found or inactive")
    return user


# PUBLIC_INTERFACE
def require_roles(*roles: str):
    """Dependency factory that enforces RBAC roles."""

    def _checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in roles:
            raise AppError(status_code=403, code="forbidden", message="Insufficient permissions")
        return current_user

    return _checker
