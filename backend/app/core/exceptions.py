from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error: str
    path: str
    timestamp: str


class APIError(Exception):
    """Base exception for API-level errors."""

    def __init__(self, message: str, error: str = "internal_server_error") -> None:
        self.message = message
        self.error = error
        super().__init__(message)


class NotFoundError(APIError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, "not_found")


class BadRequestError(APIError):
    def __init__(self, message: str = "Bad request") -> None:
        super().__init__(message, "bad_request")


class UnauthorizedError(APIError):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message, "unauthorized")


class ForbiddenError(APIError):
    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message, "forbidden")


class ConflictError(APIError):
    def __init__(self, message: str = "Conflict") -> None:
        super().__init__(message, "conflict")


class InternalServerError(APIError):
    def __init__(self, message: str = "Internal server error") -> None:
        super().__init__(message, "internal_server_error")


class DomainError(Exception):
    """Base exception for domain-level errors."""


class UserAlreadyExistsError(DomainError):
    """Raised when attempting to create a user with an existing email."""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__("A user with this email already exists")


class UserNotFoundError(DomainError):
    """Raised when a requested user does not exist."""

    def __init__(self, user_id: int | None = None) -> None:
        self.user_id = user_id
        super().__init__("User not found")


class CompanyAlreadyExistsError(DomainError):
    """Raised when attempting to create a company with an existing symbol."""

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        super().__init__("A company with this symbol already exists")


class CompanyNotFoundError(DomainError):
    """Raised when a requested company does not exist."""

    def __init__(self, company_id: int | None = None) -> None:
        self.company_id = company_id
        super().__init__("Company not found")
