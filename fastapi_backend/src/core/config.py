from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Application settings sourced from environment variables."""

    app_name: str = os.getenv("APP_NAME", "School Management System API")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    api_prefix: str = os.getenv("API_PREFIX", "/api/v1")

    # Database: we prefer POSTGRES_URL if provided by the platform.
    # If POSTGRES_URL does not contain credentials, we will inject POSTGRES_USER/PASSWORD
    # in db.session to avoid OS user mismatch.
    postgres_url: str = os.getenv("POSTGRES_URL", "")
    postgres_user: str = os.getenv("POSTGRES_USER", "")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "")

    # Security
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "CHANGE_ME_IN_ENV")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expires_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES", "30"))
    refresh_token_expires_minutes: int = int(os.getenv("REFRESH_TOKEN_EXPIRES_MINUTES", "43200"))  # 30 days

    # CORS
    cors_allow_origins: str = os.getenv("CORS_ALLOW_ORIGINS", "*")


settings = Settings()
