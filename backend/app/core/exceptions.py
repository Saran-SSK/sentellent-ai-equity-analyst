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
