from __future__ import annotations

from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PageMeta(BaseModel):
    """Pagination metadata returned alongside list results."""

    limit: int = Field(..., ge=1, le=200, description="Requested page size")
    offset: int = Field(..., ge=0, description="Requested offset")
    total: int = Field(..., ge=0, description="Total items matching the filter")


class Page(BaseModel, Generic[T]):
    """Generic paginated response container."""

    meta: PageMeta
    items: List[T]
