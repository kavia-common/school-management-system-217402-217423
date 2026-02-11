from __future__ import annotations

import urllib.parse
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.core.config import settings


def _build_database_url() -> str:
    """
    Build a DB URL for SQLAlchemy.

    We prefer POSTGRES_URL, but some environments provide it without explicit credentials.
    In that case, psycopg2 may attempt to use the OS user and fail. We inject
    POSTGRES_USER/PASSWORD (if set) into the URL.
    """
    url = settings.postgres_url
    if not url:
        raise RuntimeError("POSTGRES_URL is not set. Please configure database connection env vars.")

    user = settings.postgres_user
    password = settings.postgres_password
    if not user:
        return url

    if "://" not in url:
        return url

    scheme, rest = url.split("://", 1)

    # If URL already has credentials, keep it.
    if "@" in rest and rest.split("@", 1)[0].find("/") == -1:
        return url

    auth = urllib.parse.quote(user)
    if password:
        auth += ":" + urllib.parse.quote(password)

    return f"{scheme}://{auth}@{rest}"


engine = create_engine(_build_database_url(), pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a SQLAlchemy session and ensures it closes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
