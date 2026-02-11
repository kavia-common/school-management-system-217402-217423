from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class AppError(Exception):
    """Domain/service layer exception mapped to a consistent HTTP response."""

    status_code: int
    code: str
    message: str
    details: Optional[Any] = None
