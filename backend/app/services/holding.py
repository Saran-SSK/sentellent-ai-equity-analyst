from __future__ import annotations

from app.core.exceptions import (
    CompanyNotFoundError,
    HoldingAlreadyExistsError,
    HoldingNotFoundError,
    PortfolioNotFoundError,
)
from app.models.holding import Holding
from app.repositories.company import CompanyRepository
from app.repositories.holding import HoldingRepository
from app.repositories.portfolio import PortfolioRepository
from app.schemas.holding import HoldingCreate, HoldingUpdate


class HoldingService:
    """Business operations for holdings."""

    def __init__(
        self,
        holding_repository: HoldingRepository,
        portfolio_repository: PortfolioRepository,
        company_repository: CompanyRepository,
    ) -> None:
        self.holding_repository = holding_repository
        self.portfolio_repository = portfolio_repository
        self.company_repository = company_repository

    def create_holding(
        self,
        user_id: int,
        portfolio_id: int,
        holding: HoldingCreate,
    ) -> Holding:
        portfolio = self.portfolio_repository.get_by_id_for_user(
            portfolio_id,
            user_id,
        )

        if portfolio is None:
            raise PortfolioNotFoundError(portfolio_id)

        company = self.company_repository.get_by_id(holding.company_id)
        if company is None:
            raise CompanyNotFoundError(holding.company_id)

        existing_holding = self.holding_repository.get_by_portfolio_and_company(
            portfolio_id,
            holding.company_id,
        )

        if existing_holding is not None:
            raise HoldingAlreadyExistsError(holding.company_id)

        return self.holding_repository.create(portfolio_id, holding)

    def update_holding(
        self,
        holding_id: int,
        updates: HoldingUpdate,
    ) -> Holding:
        holding = self.holding_repository.get_by_id(holding_id)

        if holding is None:
            raise HoldingNotFoundError(holding_id)

        return self.holding_repository.update(
            holding,
            quantity=updates.quantity,
            average_buy_price=updates.average_buy_price,
            purchase_date=updates.purchase_date,
        )

    def delete_holding(
        self,
        holding_id: int,
    ) -> None:
        holding = self.holding_repository.get_by_id(holding_id)

        if holding is None:
            raise HoldingNotFoundError(holding_id)

        self.holding_repository.delete(holding)
