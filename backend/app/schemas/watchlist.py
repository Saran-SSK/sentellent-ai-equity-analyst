from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WatchlistBase(BaseModel):
    name: str


class WatchlistCreate(WatchlistBase):
    pass


class WatchlistUpdate(BaseModel):
    name: str


# ---------------- Company inside Watchlist ----------------


class CompanyInWatchlist(BaseModel):
    id: int
    symbol: str
    name: str
    exchange: str | None = None
    sector: str | None = None
    industry: str | None = None
    country: str | None = None
    currency: str | None = None

    model_config = ConfigDict(from_attributes=True)


class WatchlistCompanyRead(BaseModel):
    id: int
    watchlist_id: int
    company_id: int
    created_at: datetime
    company: CompanyInWatchlist

    model_config = ConfigDict(from_attributes=True)


# ---------------- Watchlist ----------------


class WatchlistRead(WatchlistBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    companies: list[WatchlistCompanyRead] = []

    model_config = ConfigDict(from_attributes=True)


# ---------------- Request ----------------


class WatchlistCompanyBase(BaseModel):
    company_id: int


class WatchlistCompanyCreate(WatchlistCompanyBase):
    pass
