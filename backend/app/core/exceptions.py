from __future__ import annotations

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


# ----------------------------------------------------------------------
# User
# ----------------------------------------------------------------------


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


# ----------------------------------------------------------------------
# Company
# ----------------------------------------------------------------------


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


# ----------------------------------------------------------------------
# Watchlist
# ----------------------------------------------------------------------


class WatchlistNotFoundError(DomainError):
    """Raised when a watchlist cannot be found."""

    def __init__(self, watchlist_id: int | None = None) -> None:
        self.watchlist_id = watchlist_id
        super().__init__("Watchlist not found")


class WatchlistAccessDeniedError(DomainError):
    """Raised when a user tries to access another user's watchlist."""

    def __init__(self) -> None:
        super().__init__("You do not have permission to access this watchlist")


class CompanyAlreadyInWatchlistError(DomainError):
    """Raised when attempting to add the same company twice."""

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        super().__init__("Company already exists in watchlist")


class CompanyNotInWatchlistError(DomainError):
    """Raised when removing a company that is not present."""

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        super().__init__("Company not found in watchlist")


# ----------------------------------------------------------------------
# Portfolio
# ----------------------------------------------------------------------


class PortfolioNotFoundError(DomainError):
    """Raised when a portfolio cannot be found."""

    def __init__(self, portfolio_id: int | None = None) -> None:
        self.portfolio_id = portfolio_id
        super().__init__("Portfolio not found")


class HoldingNotFoundError(DomainError):
    """Raised when a holding cannot be found."""

    def __init__(self, holding_id: int | None = None) -> None:
        self.holding_id = holding_id
        super().__init__("Holding not found")


class HoldingAlreadyExistsError(DomainError):
    """Raised when attempting to add a holding that already exists."""

    def __init__(self, company_id: int) -> None:
        self.company_id = company_id
        super().__init__("Holding already exists in portfolio")
