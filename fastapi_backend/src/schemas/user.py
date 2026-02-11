from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserPublic(BaseModel):
    """Public user representation."""

    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    """Create user payload."""

    email: EmailStr = Field(..., description="Unique email")
    full_name: str = Field("", max_length=200, description="Full name")
    password: str = Field(..., min_length=8, max_length=200, description="Plaintext password (will be hashed)")
    role: str = Field("admin", description="Role: admin|teacher|student|parent")
    is_active: bool = Field(True, description="Whether the user can authenticate")


class UserUpdate(BaseModel):
    """Update user payload (partial)."""

    full_name: str | None = Field(None, max_length=200)
    password: str | None = Field(None, min_length=8, max_length=200)
    role: str | None = Field(None)
    is_active: bool | None = Field(None)
