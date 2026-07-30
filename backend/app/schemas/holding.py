from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class HoldingCreate(BaseModel):
    company_id: int
    quantity: int
    average_buy_price: float
    purchase_date: date | None = None


class HoldingUpdate(BaseModel):
    quantity: int | None = None
    average_buy_price: float | None = None
    purchase_date: date | None = None
