from __future__ import annotations

from app.core import security
from app.core.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Business operations for users."""

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def create_user(self, user: UserCreate) -> User:
        existing_user = self.user_repository.get_by_email(str(user.email))
        if existing_user is not None:
            raise UserAlreadyExistsError(str(user.email))

        hashed_password = security.hash_password(user.password)
        return self.user_repository.create(
            user=user,
            hashed_password=hashed_password,
        )

    def get_user(self, id: int) -> User:
        user = self.user_repository.get_by_id(id)
        if user is None:
            raise UserNotFoundError(id)

        return user

    def get_user_by_email(self, email: str) -> User | None:
        return self.user_repository.get_by_email(email)

    def authenticate_user(self, email: str, password: str) -> User | None:
        print("Email received:", repr(email))

        user = self.user_repository.get_by_email(email)
        print("User found:", user)

        if user is None:
            return None

        print("Stored hash:", user.hashed_password)

        ok = security.verify_password(password, user.hashed_password)
        print("Password verified:", ok)

        if not ok:
            return None

        return user

    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.user_repository.list_users(skip=skip, limit=limit)

    def update_user(self, id: int, updates: UserUpdate) -> User:
        user = self.get_user(id)
        update_data = updates.model_dump(exclude_unset=True)

        password = update_data.pop("password", None)
        if password is not None:
            update_data["hashed_password"] = security.hash_password(password)

        return self.user_repository.update(
            user=user,
            updates=update_data,
        )

    def delete_user(self, id: int) -> None:
        user = self.get_user(id)
        self.user_repository.delete(user)
