from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schemas.auth import LoginRequest, RefreshRequest, TokenPair
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenPair,
    summary="Login",
    description="Authenticate a user using email/password and return access + refresh JWT tokens.",
    operation_id="auth_login",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenPair:
    service = AuthService(db)
    access, refresh = service.login(email=str(payload.email), password=payload.password)
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post(
    "/refresh",
    response_model=TokenPair,
    summary="Refresh token",
    description="Exchange a refresh token for a new access + refresh token pair.",
    operation_id="auth_refresh",
)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenPair:
    service = AuthService(db)
    access, refresh_token = service.refresh(payload.refresh_token)
    return TokenPair(access_token=access, refresh_token=refresh_token)
