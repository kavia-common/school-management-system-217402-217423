from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.errors import AppError
from src.models.student import Student


class StudentService:
    """Student management use-cases."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, *, admission_no: str, full_name: str, date_of_birth=None, grade=None, section=None) -> Student:
        existing = self.db.scalar(select(Student).where(Student.admission_no == admission_no))
        if existing:
            raise AppError(status_code=409, code="admission_no_taken", message="Admission number already exists")

        student = Student(
            admission_no=admission_no,
            full_name=full_name,
            date_of_birth=date_of_birth,
            grade=grade,
            section=section,
        )
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

    def list(self, *, limit: int, offset: int, q: str | None, grade: str | None) -> tuple[list[Student], int]:
        stmt = select(Student)
        count_stmt = select(Student)

        if q:
            like = f"%{q.lower()}%"
            stmt = stmt.where(Student.full_name.ilike(like) | Student.admission_no.ilike(like))
            count_stmt = count_stmt.where(Student.full_name.ilike(like) | Student.admission_no.ilike(like))
        if grade:
            stmt = stmt.where(Student.grade == grade)
            count_stmt = count_stmt.where(Student.grade == grade)

        total = self.db.execute(count_stmt).scalars().all()
        total_count = len(total)

        items = self.db.execute(stmt.order_by(Student.created_at.desc()).limit(limit).offset(offset)).scalars().all()
        return items, total_count

    def get(self, student_id) -> Student:
        student = self.db.get(Student, student_id)
        if not student:
            raise AppError(status_code=404, code="not_found", message="Student not found")
        return student

    def update(self, student_id, *, full_name=None, date_of_birth=None, grade=None, section=None) -> Student:
        student = self.get(student_id)

        if full_name is not None:
            student.full_name = full_name
        if date_of_birth is not None:
            student.date_of_birth = date_of_birth
        if grade is not None:
            student.grade = grade
        if section is not None:
            student.section = section

        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

    def delete(self, student_id) -> None:
        student = self.get(student_id)
        self.db.delete(student)
        self.db.commit()
