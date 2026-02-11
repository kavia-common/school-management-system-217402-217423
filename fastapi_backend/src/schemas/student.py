from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class StudentPublic(BaseModel):
    id: uuid.UUID
    admission_no: str
    full_name: str
    date_of_birth: date | None
    grade: str | None
    section: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class StudentCreate(BaseModel):
    admission_no: str = Field(..., min_length=1, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=200)
    date_of_birth: date | None = None
    grade: str | None = Field(None, max_length=50)
    section: str | None = Field(None, max_length=50)


class StudentUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=200)
    date_of_birth: date | None = None
    grade: str | None = Field(None, max_length=50)
    section: str | None = Field(None, max_length=50)
