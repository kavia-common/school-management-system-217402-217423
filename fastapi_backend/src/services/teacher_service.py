from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.errors import AppError
from src.models.teacher import Teacher


class TeacherService:
    """Teacher management use-cases."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, *, employee_no: str, full_name: str, department=None) -> Teacher:
        existing = self.db.scalar(select(Teacher).where(Teacher.employee_no == employee_no))
        if existing:
            raise AppError(status_code=409, code="employee_no_taken", message="Employee number already exists")

        teacher = Teacher(employee_no=employee_no, full_name=full_name, department=department)
        self.db.add(teacher)
        self.db.commit()
        self.db.refresh(teacher)
        return teacher

    def list(self, *, limit: int, offset: int, q: str | None, department: str | None) -> tuple[list[Teacher], int]:
        stmt = select(Teacher)
        count_stmt = select(Teacher)

        if q:
            like = f"%{q.lower()}%"
            stmt = stmt.where(Teacher.full_name.ilike(like) | Teacher.employee_no.ilike(like))
            count_stmt = count_stmt.where(Teacher.full_name.ilike(like) | Teacher.employee_no.ilike(like))
        if department:
            stmt = stmt.where(Teacher.department == department)
            count_stmt = count_stmt.where(Teacher.department == department)

        total = self.db.execute(count_stmt).scalars().all()
        total_count = len(total)

        items = self.db.execute(stmt.order_by(Teacher.created_at.desc()).limit(limit).offset(offset)).scalars().all()
        return items, total_count

    def get(self, teacher_id) -> Teacher:
        teacher = self.db.get(Teacher, teacher_id)
        if not teacher:
            raise AppError(status_code=404, code="not_found", message="Teacher not found")
        return teacher

    def update(self, teacher_id, *, full_name=None, department=None) -> Teacher:
        teacher = self.get(teacher_id)

        if full_name is not None:
            teacher.full_name = full_name
        if department is not None:
            teacher.department = department

        self.db.add(teacher)
        self.db.commit()
        self.db.refresh(teacher)
        return teacher

    def delete(self, teacher_id) -> None:
        teacher = self.get(teacher_id)
        self.db.delete(teacher)
        self.db.commit()
