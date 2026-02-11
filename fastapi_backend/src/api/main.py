from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routers.auth import router as auth_router
from src.api.routers.students import router as students_router
from src.api.routers.teachers import router as teachers_router
from src.api.routers.users import router as users_router
from src.core.config import settings
from src.core.errors import AppError

openapi_tags = [
    {"name": "auth", "description": "Authentication endpoints (login/refresh)."},
    {"name": "users", "description": "User management (admin-only)."},
    {"name": "students", "description": "Student management."},
    {"name": "teachers", "description": "Teacher management."},
]

app = FastAPI(
    title=settings.app_name,
    description="Backend API for the School Management System. Implements JWT authentication, RBAC and CRUD modules.",
    version=settings.app_version,
    openapi_tags=openapi_tags,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_allow_origins.split(",")] if settings.cors_allow_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(Exception)
def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    # Avoid leaking internal details; keep a consistent envelope
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": "Internal server error"}},
    )


@app.get("/", summary="Health check", description="Service health endpoint.", tags=["health"], operation_id="health_check")
def health_check():
    return {"message": "Healthy"}


# API v1 routes
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(users_router, prefix=settings.api_prefix)
app.include_router(students_router, prefix=settings.api_prefix)
app.include_router(teachers_router, prefix=settings.api_prefix)
