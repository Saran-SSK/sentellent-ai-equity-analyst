from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Shared user fields."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr = Field(..., max_length=255)
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    """Fields accepted when creating a user."""

    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """Fields accepted when updating a user."""

    model_config = ConfigDict(extra="forbid")

    email: EmailStr | None = Field(default=None, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    is_active: bool | None = None


class UserRead(UserBase):
    """User fields returned by the API."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
