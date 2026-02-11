from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TeacherPublic(BaseModel):
    id: uuid.UUID
    employee_no: str
    full_name: str
    department: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TeacherCreate(BaseModel):
    employee_no: str = Field(..., min_length=1, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=200)
    department: str | None = Field(None, max_length=100)


class TeacherUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=200)
    department: str | None = Field(None, max_length=100)
