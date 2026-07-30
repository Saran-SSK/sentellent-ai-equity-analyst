from __future__ import annotations

from app.core.exceptions import PortfolioNotFoundError
from app.models.portfolio import Portfolio
from app.repositories.portfolio import PortfolioRepository
from app.schemas.portfolio import PortfolioCreate, PortfolioUpdate


class PortfolioService:
    """Business operations for portfolios."""

    def __init__(
        self,
        portfolio_repository: PortfolioRepository,
    ) -> None:
        self.portfolio_repository = portfolio_repository

    def create_portfolio(
        self,
        user_id: int,
        portfolio: PortfolioCreate,
    ) -> Portfolio:
        return self.portfolio_repository.create(user_id, portfolio)

    def get_portfolio(
        self,
        user_id: int,
        portfolio_id: int,
    ) -> Portfolio:
        portfolio = self.portfolio_repository.get_by_id_for_user(
            portfolio_id,
            user_id,
        )

        if portfolio is None:
            raise PortfolioNotFoundError(portfolio_id)

        return portfolio

    def list_portfolios(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Portfolio]:
        return self.portfolio_repository.list_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit,
        )

    def update_portfolio(
        self,
        user_id: int,
        portfolio_id: int,
        updates: PortfolioUpdate,
    ) -> Portfolio:
        portfolio = self.get_portfolio(user_id, portfolio_id)
        return self.portfolio_repository.update(portfolio, updates.name)

    def delete_portfolio(
        self,
        user_id: int,
        portfolio_id: int,
    ) -> None:
        portfolio = self.get_portfolio(user_id, portfolio_id)
        self.portfolio_repository.delete(portfolio)
