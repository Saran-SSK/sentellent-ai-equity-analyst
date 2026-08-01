from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InvestorProfileBase(BaseModel):
    risk_profile: str | None = None
    investment_horizon: str | None = None
    investment_style: str | None = None
    preferred_market: str | None = None
    preferred_sectors: str | None = None
    notes: str | None = None


class InvestorProfileCreate(InvestorProfileBase):
    pass


class InvestorProfileUpdate(InvestorProfileBase):
    pass


class InvestorProfileRead(InvestorProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
