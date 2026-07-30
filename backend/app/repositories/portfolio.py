from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.schemas.portfolio import PortfolioCreate


class PortfolioRepository:
    """Database operations for portfolios."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, portfolio_id: int) -> Portfolio | None:
        statement = (
            select(Portfolio)
            .options(
                selectinload(Portfolio.holdings).selectinload(Holding.company)
            )
            .where(Portfolio.id == portfolio_id)
        )
        return self.session.execute(statement).scalar_one_or_none()

    def get_by_id_for_user(
        self,
        portfolio_id: int,
        user_id: int,
    ) -> Portfolio | None:
        statement = (
            select(Portfolio)
            .options(
                selectinload(Portfolio.holdings).selectinload(Holding.company)
            )
            .where(
                Portfolio.id == portfolio_id,
                Portfolio.user_id == user_id,
            )
        )
        return self.session.execute(statement).scalar_one_or_none()

    def list_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Portfolio]:
        statement = (
            select(Portfolio)
            .options(
                selectinload(Portfolio.holdings).selectinload(Holding.company)
            )
            .where(Portfolio.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Portfolio.id)
        )
        return list(self.session.execute(statement).scalars().all())

    def create(
        self,
        user_id: int,
        portfolio: PortfolioCreate,
    ) -> Portfolio:
        db_portfolio = Portfolio(
            user_id=user_id,
            **portfolio.model_dump(),
        )
        self.session.add(db_portfolio)
        self.session.commit()
        self.session.refresh(db_portfolio)
        return db_portfolio

    def update(self, portfolio: Portfolio, name: str) -> Portfolio:
        portfolio.name = name
        self.session.add(portfolio)
        self.session.commit()
        self.session.refresh(portfolio)
        return portfolio

    def delete(self, portfolio: Portfolio) -> None:
        self.session.delete(portfolio)
        self.session.commit()
