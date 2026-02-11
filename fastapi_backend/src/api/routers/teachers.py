from __future__ import annotations

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.deps import require_roles
from src.core.pagination import Page, PageMeta
from src.db.session import get_db
from src.schemas.teacher import TeacherCreate, TeacherPublic, TeacherUpdate
from src.services.teacher_service import TeacherService

router = APIRouter(prefix="/teachers", tags=["teachers"])


@router.post(
    "",
    response_model=TeacherPublic,
    summary="Create teacher",
    description="Create a teacher (admin-only).",
    operation_id="teachers_create",
)
def create_teacher(
    payload: TeacherCreate,
    db: Session = Depends(get_db),
    _: Annotated[object, Depends(require_roles("admin"))] = None,
) -> TeacherPublic:
    service = TeacherService(db)
    teacher = service.create(employee_no=payload.employee_no, full_name=payload.full_name, department=payload.department)
    return TeacherPublic.model_validate(teacher)


@router.get(
    "",
    response_model=Page[TeacherPublic],
    summary="List teachers",
    description="List teachers (admin) with pagination and optional filtering.",
    operation_id="teachers_list",
)
def list_teachers(
    db: Session = Depends(get_db),
    _: Annotated[object, Depends(require_roles("admin"))] = None,
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    q: Optional[str] = Query(None, description="Search by full_name/employee_no"),
    department: Optional[str] = Query(None, description="Filter by department"),
) -> Page[TeacherPublic]:
    service = TeacherService(db)
    items, total = service.list(limit=limit, offset=offset, q=q, department=department)
    return Page[TeacherPublic](
        meta=PageMeta(limit=limit, offset=offset, total=total),
        items=[TeacherPublic.model_validate(t) for t in items],
    )


@router.get(
    "/{teacher_id}",
    response_model=TeacherPublic,
    summary="Get teacher",
    description="Get teacher (admin).",
    operation_id="teachers_get",
)
def get_teacher(
    teacher_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Annotated[object, Depends(require_roles("admin"))] = None,
) -> TeacherPublic:
    service = TeacherService(db)
    item = service.get(teacher_id)
    return TeacherPublic.model_validate(item)


@router.patch(
    "/{teacher_id}",
    response_model=TeacherPublic,
    summary="Update teacher",
    description="Update teacher (admin-only).",
    operation_id="teachers_update",
)
def update_teacher(
    teacher_id: uuid.UUID,
    payload: TeacherUpdate,
    db: Session = Depends(get_db),
    _: Annotated[object, Depends(require_roles("admin"))] = None,
) -> TeacherPublic:
    service = TeacherService(db)
    item = service.update(teacher_id, full_name=payload.full_name, department=payload.department)
    return TeacherPublic.model_validate(item)


@router.delete(
    "/{teacher_id}",
    summary="Delete teacher",
    description="Delete teacher (admin-only).",
    operation_id="teachers_delete",
)
def delete_teacher(
    teacher_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Annotated[object, Depends(require_roles("admin"))] = None,
) -> dict:
    service = TeacherService(db)
    service.delete(teacher_id)
    return {"deleted": True}
