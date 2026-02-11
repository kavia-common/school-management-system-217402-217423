from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class TokenPair(BaseModel):
    """Login/refresh response containing both access and refresh tokens."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")


class LoginRequest(BaseModel):
    """Login request payload."""

    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, max_length=200, description="User password")


class RefreshRequest(BaseModel):
    """Refresh request payload."""

    refresh_token: str = Field(..., description="JWT refresh token")
