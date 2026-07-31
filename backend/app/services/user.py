from __future__ import annotations

from sqlalchemy.exc import IntegrityError

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

    def get_or_create_google_user(
        self,
        google_id: str,
        email: str,
        full_name: str | None = None,
        google_avatar_url: str | None = None,
    ) -> User:
        """Get existing user by Google ID or email, or create a new one."""
        # Try to find user by Google ID first
        user = self.user_repository.get_by_google_id(google_id)
        if user:
            # Update user info if changed
            update_data = {}
            if full_name and user.full_name != full_name:
                update_data["full_name"] = full_name
            if google_avatar_url and user.google_avatar_url != google_avatar_url:
                update_data["google_avatar_url"] = google_avatar_url
            if update_data:
                user = self.user_repository.update(user=user, updates=update_data)
            return user

        # Try to find user by email (in case they previously registered with password)
        user = self.user_repository.get_by_email(email)
        if user:
            # Link Google account to existing user
            update_data = {
                "google_id": google_id,
            }
            if full_name and not user.full_name:
                update_data["full_name"] = full_name
            if google_avatar_url and not user.google_avatar_url:
                update_data["google_avatar_url"] = google_avatar_url
            return self.user_repository.update(user=user, updates=update_data)

        # Create new user with Google OAuth
        try:
            return self.user_repository.create(
                email=email,
                full_name=full_name,
                google_id=google_id,
                google_avatar_url=google_avatar_url,
                hashed_password=None,  # No password for OAuth users
            )
        except IntegrityError:
            # Handle race condition: user might have been created by another request
            # Retry lookup to get the existing user
            self.user_repository.session.rollback()
            
            # Check again by Google ID (might have been created by another request)
            user = self.user_repository.get_by_google_id(google_id)
            if user:
                return user
            
            # Check again by email (might have been created by another request)
            user = self.user_repository.get_by_email(email)
            if user:
                # Update with Google ID if missing
                if not user.google_id:
                    return self.user_repository.update(
                        user=user,
                        updates={"google_id": google_id}
                    )
                return user
            
            # If still not found, re-raise the error
            raise
