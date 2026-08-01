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
from app.repositories.watchlist import WatchlistRepository
from app.repositories.portfolio import PortfolioRepository
from app.repositories.holding import HoldingRepository
from app.repositories.investor_profile import InvestorProfileRepository
from app.services.company import CompanyService
from app.services.user import UserService
from app.services.watchlist import WatchlistService
from app.services.portfolio import PortfolioService
from app.services.holding import HoldingService
from app.services.investor_profile import InvestorProfileService
from app.agents.context_builder import ContextBuilder


def get_watchlist_repository(
    db: Annotated[Session, Depends(get_db)],
) -> WatchlistRepository:
    return WatchlistRepository(db)


def get_watchlist_service(
    watchlist_repository: Annotated[
        WatchlistRepository,
        Depends(get_watchlist_repository),
    ],
    company_repository: Annotated[
        CompanyRepository,
        Depends(get_company_repository),
    ],
) -> WatchlistService:
    return WatchlistService(
        watchlist_repository,
        company_repository,
    )


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


def get_company_repository(
    db: Annotated[Session, Depends(get_db)],
) -> CompanyRepository:
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
    market_provider: Annotated[
        MarketDataProvider, Depends(get_market_provider_dependency)
    ],
) -> CompanyService:
    """Dependency that creates a CompanyService instance.

    Args:
        company_repository: Injected CompanyRepository.
        market_provider: Injected MarketDataProvider.

    Returns:
        A CompanyService configured with the provided repository and market provider.
    """
    return CompanyService(company_repository, market_provider)


def get_portfolio_repository(
    db: Annotated[Session, Depends(get_db)],
) -> PortfolioRepository:
    """Dependency that creates a PortfolioRepository instance.

    Args:
        db: Injected database session.

    Returns:
        A PortfolioRepository bound to the current session.
    """
    return PortfolioRepository(db)


def get_holding_repository(
    db: Annotated[Session, Depends(get_db)],
) -> HoldingRepository:
    """Dependency that creates a HoldingRepository instance.

    Args:
        db: Injected database session.

    Returns:
        A HoldingRepository bound to the current session.
    """
    return HoldingRepository(db)


def get_portfolio_service(
    portfolio_repository: Annotated[
        PortfolioRepository,
        Depends(get_portfolio_repository),
    ],
) -> PortfolioService:
    """Dependency that creates a PortfolioService instance.

    Args:
        portfolio_repository: Injected PortfolioRepository.

    Returns:
        A PortfolioService configured with the provided repository.
    """
    return PortfolioService(portfolio_repository)


def get_holding_service(
    holding_repository: Annotated[
        HoldingRepository,
        Depends(get_holding_repository),
    ],
    portfolio_repository: Annotated[
        PortfolioRepository,
        Depends(get_portfolio_repository),
    ],
    company_repository: Annotated[
        CompanyRepository,
        Depends(get_company_repository),
    ],
) -> HoldingService:
    """Dependency that creates a HoldingService instance.

    Args:
        holding_repository: Injected HoldingRepository.
        portfolio_repository: Injected PortfolioRepository.
        company_repository: Injected CompanyRepository.

    Returns:
        A HoldingService configured with the provided repositories.
    """
    return HoldingService(
        holding_repository,
        portfolio_repository,
        company_repository,
    )


def get_investor_profile_repository(
    db: Annotated[Session, Depends(get_db)],
) -> InvestorProfileRepository:
    """Dependency that creates an InvestorProfileRepository instance.

    Args:
        db: Injected database session.

    Returns:
        An InvestorProfileRepository bound to the current session.
    """
    return InvestorProfileRepository(db)


def get_investor_profile_service(
    investor_profile_repository: Annotated[
        InvestorProfileRepository,
        Depends(get_investor_profile_repository),
    ],
) -> InvestorProfileService:
    """Dependency that creates an InvestorProfileService instance.

    Args:
        investor_profile_repository: Injected InvestorProfileRepository.

    Returns:
        An InvestorProfileService configured with the provided repository.
    """
    return InvestorProfileService(investor_profile_repository)


def get_context_builder(
    investor_profile_service: Annotated[
        InvestorProfileService,
        Depends(get_investor_profile_service),
    ],
    portfolio_service: Annotated[
        PortfolioService,
        Depends(get_portfolio_service),
    ],
    watchlist_service: Annotated[
        WatchlistService,
        Depends(get_watchlist_service),
    ],
) -> ContextBuilder:
    """Dependency that creates a ContextBuilder instance.

    Args:
        investor_profile_service: Injected InvestorProfileService.
        portfolio_service: Injected PortfolioService.
        watchlist_service: Injected WatchlistService.

    Returns:
        A ContextBuilder configured with the provided services.
    """
    return ContextBuilder(
        investor_profile_service,
        portfolio_service,
        watchlist_service,
    )
