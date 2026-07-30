from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.holding import Holding
from app.schemas.holding import HoldingCreate


class HoldingRepository:
    """Database operations for holdings."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, holding_id: int) -> Holding | None:
        statement = (
            select(Holding)
            .options(selectinload(Holding.company))
            .where(Holding.id == holding_id)
        )
        return self.session.execute(statement).scalar_one_or_none()

    def get_by_portfolio_and_company(
        self,
        portfolio_id: int,
        company_id: int,
    ) -> Holding | None:
        statement = select(Holding).where(
            Holding.portfolio_id == portfolio_id,
            Holding.company_id == company_id,
        )
        return self.session.execute(statement).scalar_one_or_none()

    def create(
        self,
        portfolio_id: int,
        holding: HoldingCreate,
    ) -> Holding:
        db_holding = Holding(
            portfolio_id=portfolio_id,
            **holding.model_dump(),
        )
        self.session.add(db_holding)
        self.session.commit()
        self.session.refresh(db_holding)
        return db_holding

    def update(
        self,
        holding: Holding,
        quantity: int | None = None,
        average_buy_price: float | None = None,
        purchase_date: date | None = None,
    ) -> Holding:
        if quantity is not None:
            holding.quantity = quantity
        if average_buy_price is not None:
            holding.average_buy_price = average_buy_price
        if purchase_date is not None:
            holding.purchase_date = purchase_date

        self.session.add(holding)
        self.session.commit()
        self.session.refresh(holding)
        return holding

    def delete(self, holding: Holding) -> None:
        self.session.delete(holding)
        self.session.commit()
