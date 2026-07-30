from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class HoldingCompanyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    name: str


class HoldingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quantity: int
    average_buy_price: float
    purchase_date: date | None

    company: HoldingCompanyRead


class PortfolioCreate(BaseModel):
    name: str


class PortfolioUpdate(BaseModel):
    name: str


class PortfolioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str

    created_at: datetime
    updated_at: datetime

    holdings: list[HoldingRead] = []
