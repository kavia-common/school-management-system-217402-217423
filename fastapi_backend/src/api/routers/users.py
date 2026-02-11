from __future__ import annotations

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.deps import require_roles
from src.core.pagination import Page, PageMeta
from src.db.session import get_db
from src.schemas.user import UserCreate, UserPublic, UserUpdate
from src.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserPublic,
    summary="Create user",
    description="Create a new user (admin-only). Password is hashed server-side.",
    operation_id="users_create",
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: Annotated[object, Depends(require_roles("admin"))] = None,
) -> UserPublic:
    service = UserService(db)
    user = service.create_user(
        email=str(payload.email),
        full_name=payload.full_name,
        password=payload.password,
        role=payload.role,
        is_active=payload.is_active,
    )
    return UserPublic.model_validate(user)


@router.get(
    "",
    response_model=Page[UserPublic],
    summary="List users",
    description="List users (admin-only) with pagination and optional query filter (q matches email/full_name).",
    operation_id="users_list",
)
def list_users(
    db: Session = Depends(get_db),
    _: Annotated[object, Depends(require_roles("admin"))] = None,
    limit: int = Query(20, ge=1, le=200, description="Page size"),
    offset: int = Query(0, ge=0, description="Offset"),
    q: Optional[str] = Query(None, description="Search term for email/full_name"),
) -> Page[UserPublic]:
    service = UserService(db)
    users, total = service.list_users(limit=limit, offset=offset, q=q)
    return Page[UserPublic](
        meta=PageMeta(limit=limit, offset=offset, total=total),
        items=[UserPublic.model_validate(u) for u in users],
    )


@router.get(
    "/{user_id}",
    response_model=UserPublic,
    summary="Get user",
    description="Get a single user (admin-only).",
    operation_id="users_get",
)
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Annotated[object, Depends(require_roles("admin"))] = None,
) -> UserPublic:
    service = UserService(db)
    user = service.get_user(user_id)
    return UserPublic.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserPublic,
    summary="Update user",
    description="Update a user (admin-only). Only provided fields are updated.",
    operation_id="users_update",
)
def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _: Annotated[object, Depends(require_roles("admin"))] = None,
) -> UserPublic:
    service = UserService(db)
    user = service.update_user(
        user_id,
        full_name=payload.full_name,
        password=payload.password,
        role=payload.role,
        is_active=payload.is_active,
    )
    return UserPublic.model_validate(user)


@router.delete(
    "/{user_id}",
    summary="Delete user",
    description="Delete a user (admin-only).",
    operation_id="users_delete",
)
def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Annotated[object, Depends(require_roles("admin"))] = None,
) -> dict:
    service = UserService(db)
    service.delete_user(user_id)
    return {"deleted": True}
