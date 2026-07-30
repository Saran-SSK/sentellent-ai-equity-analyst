from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.providers.market.base import MarketDataProvider
from app.providers.market.provider import get_market_provider
from app.repositories.company import CompanyRepository
from app.repositories.user import UserRepository
from app.services.company import CompanyService
from app.services.user import UserService


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a SQLAlchemy database session.

    Yields:
        A database session that is closed automatically after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_repository(db: Annotated[Session, Depends(get_db)]) -> UserRepository:
    """Dependency that creates a UserRepository instance.

    Args:
        db: Injected database session.

    Returns:
        A UserRepository bound to the current session.
    """
    return UserRepository(db)


def get_company_repository(db: Annotated[Session, Depends(get_db)]) -> CompanyRepository:
    """Dependency that creates a CompanyRepository instance.

    Args:
        db: Injected database session.

    Returns:
        A CompanyRepository bound to the current session.
    """
    return CompanyRepository(db)


def get_market_provider_dependency() -> MarketDataProvider:
    """Dependency that provides the active market data provider.

    Returns:
        The singleton MarketDataProvider instance configured by the
        get_market_provider factory.
    """
    return get_market_provider()


def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    """Dependency that creates a UserService instance.

    Args:
        user_repository: Injected UserRepository.

    Returns:
        A UserService configured with the provided repository.
    """
    return UserService(user_repository)


def get_company_service(
    company_repository: Annotated[CompanyRepository, Depends(get_company_repository)],
    market_provider: Annotated[MarketDataProvider, Depends(get_market_provider_dependency)],
) -> CompanyService:
    """Dependency that creates a CompanyService instance.

    Args:
        company_repository: Injected CompanyRepository.
        market_provider: Injected MarketDataProvider.

    Returns:
        A CompanyService configured with the provided repository and market provider.
    """
    return CompanyService(company_repository, market_provider)
