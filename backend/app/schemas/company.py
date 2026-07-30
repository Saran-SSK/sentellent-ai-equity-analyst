from __future__ import annotations

from datetime import datetime

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, field_validator


class CompanyValidationBase(BaseModel):
    """Shared validators for company normalization."""

    model_config = ConfigDict(extra="forbid")

    @field_validator("symbol", check_fields=False)
    @classmethod
    def normalize_symbol(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().upper()

    @field_validator("currency", check_fields=False)
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().upper()


class CompanyBase(CompanyValidationBase):
    """Shared company fields."""

    symbol: str = Field(..., min_length=1, max_length=32)
    name: str = Field(..., min_length=1, max_length=255)
    exchange: str | None = Field(default=None, max_length=100)
    sector: str | None = Field(default=None, max_length=150)
    industry: str | None = Field(default=None, max_length=150)
    country: str | None = Field(default=None, max_length=100)
    currency: str | None = Field(default=None, max_length=10)
    description: str | None = None
    website: AnyUrl | None = Field(default=None, max_length=500)


class CompanyCreate(CompanyBase):
    """Fields accepted when creating a company."""


class CompanyUpdate(CompanyValidationBase):
    """Fields accepted when updating a company."""

    model_config = ConfigDict(extra="forbid")

    symbol: str | None = Field(default=None, min_length=1, max_length=32)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    exchange: str | None = Field(default=None, max_length=100)
    sector: str | None = Field(default=None, max_length=150)
    industry: str | None = Field(default=None, max_length=150)
    country: str | None = Field(default=None, max_length=100)
    currency: str | None = Field(default=None, max_length=10)
    description: str | None = None
    website: AnyUrl | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class CompanyRead(CompanyBase):
    """Company fields returned by the API."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
