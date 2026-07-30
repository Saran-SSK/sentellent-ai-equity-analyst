from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:
    """Database operations for users."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, id: int) -> User | None:
        statement = select(User).where(User.id == id)
        return self.session.execute(statement).scalar_one_or_none()

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.session.execute(statement).scalar_one_or_none()

    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        statement = select(User).offset(skip).limit(limit)
        return list(self.session.execute(statement).scalars().all())

    def create(self, user: UserCreate, hashed_password: str) -> User:
        db_user = User(
            **user.model_dump(exclude={"password"}),
            hashed_password=hashed_password,
        )
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def update(self, user: User, updates: BaseModel | Mapping[str, Any]) -> User:
        update_data = self._to_update_data(updates)

        for field, value in update_data.items():
            setattr(user, field, value)

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.session.delete(user)
        self.session.commit()

    @staticmethod
    def _to_update_data(updates: BaseModel | Mapping[str, Any]) -> dict[str, Any]:
        if isinstance(updates, BaseModel):
            data = updates.model_dump(exclude_unset=True)
        else:
            data = dict(updates)

        writable_fields = {
            "email",
            "full_name",
            "hashed_password",
            "is_active",
            "is_superuser",
        }
        return {key: value for key, value in data.items() if key in writable_fields}
