from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.errors import AppError
from src.core.security import hash_password
from src.models.user import User


class UserService:
    """User management use-cases."""

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, *, email: str, full_name: str, password: str, role: str, is_active: bool) -> User:
        existing = self.db.scalar(select(User).where(User.email == email))
        if existing:
            raise AppError(status_code=409, code="email_taken", message="Email already exists")

        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            role=role,
            is_active=is_active,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_users(self, *, limit: int, offset: int, q: str | None) -> tuple[list[User], int]:
        stmt = select(User)
        count_stmt = select(User)

        if q:
            like = f"%{q.lower()}%"
            stmt = stmt.where(User.email.ilike(like) | User.full_name.ilike(like))
            count_stmt = count_stmt.where(User.email.ilike(like) | User.full_name.ilike(like))

        total = self.db.execute(count_stmt).scalars().all()
        total_count = len(total)

        users = self.db.execute(stmt.order_by(User.created_at.desc()).limit(limit).offset(offset)).scalars().all()
        return users, total_count

    def get_user(self, user_id) -> User:
        user = self.db.get(User, user_id)
        if not user:
            raise AppError(status_code=404, code="not_found", message="User not found")
        return user

    def update_user(self, user_id, *, full_name=None, password=None, role=None, is_active=None) -> User:
        user = self.get_user(user_id)

        if full_name is not None:
            user.full_name = full_name
        if password is not None:
            user.hashed_password = hash_password(password)
        if role is not None:
            user.role = role
        if is_active is not None:
            user.is_active = is_active

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id) -> None:
        user = self.get_user(user_id)
        self.db.delete(user)
        self.db.commit()
