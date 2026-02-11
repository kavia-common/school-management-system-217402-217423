from __future__ import annotations

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.deps import require_roles
from src.core.pagination import Page, PageMeta
from src.db.session import get_db
from src.schemas.student import StudentCreate, StudentPublic, StudentUpdate
from src.services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["students"])


@router.post(
    "",
    response_model=StudentPublic,
    summary="Create student",
    description="Create a student (admin-only).",
    operation_id="students_create",
)
def create_student(
    payload: StudentCreate,
    db: Session = Depends(get_db),
    _: Annotated[object, Depends(require_roles("admin"))] = None,
) -> StudentPublic:
    service = StudentService(db)
    student = service.create(
        admission_no=payload.admission_no,
        full_name=payload.full_name,
        date_of_birth=payload.date_of_birth,
        grade=payload.grade,
        section=payload.section,
    )
    return StudentPublic.model_validate(student)


@router.get(
    "",
    response_model=Page[StudentPublic],
    summary="List students",
    description="List students (admin, teacher) with pagination and optional filtering.",
    operation_id="students_list",
)
def list_students(
    db: Session = Depends(get_db),
    _: Annotated[object, Depends(require_roles("admin", "teacher"))] = None,
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    q: Optional[str] = Query(None, description="Search by full_name/admission_no"),
    grade: Optional[str] = Query(None, description="Filter by grade"),
) -> Page[StudentPublic]:
    service = StudentService(db)
    items, total = service.list(limit=limit, offset=offset, q=q, grade=grade)
    return Page[StudentPublic](
        meta=PageMeta(limit=limit, offset=offset, total=total),
        items=[StudentPublic.model_validate(s) for s in items],
    )


@router.get(
    "/{student_id}",
    response_model=StudentPublic,
    summary="Get student",
    description="Get a student (admin, teacher).",
    operation_id="students_get",
)
def get_student(
    student_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Annotated[object, Depends(require_roles("admin", "teacher"))] = None,
) -> StudentPublic:
    service = StudentService(db)
    item = service.get(student_id)
    return StudentPublic.model_validate(item)


@router.patch(
    "/{student_id}",
    response_model=StudentPublic,
    summary="Update student",
    description="Update student (admin-only).",
    operation_id="students_update",
)
def update_student(
    student_id: uuid.UUID,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
    _: Annotated[object, Depends(require_roles("admin"))] = None,
) -> StudentPublic:
    service = StudentService(db)
    item = service.update(
        student_id,
        full_name=payload.full_name,
        date_of_birth=payload.date_of_birth,
        grade=payload.grade,
        section=payload.section,
    )
    return StudentPublic.model_validate(item)


@router.delete(
    "/{student_id}",
    summary="Delete student",
    description="Delete student (admin-only).",
    operation_id="students_delete",
)
def delete_student(
    student_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Annotated[object, Depends(require_roles("admin"))] = None,
) -> dict:
    service = StudentService(db)
    service.delete(student_id)
    return {"deleted": True}
