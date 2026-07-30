from __future__ import annotations

from app.core.exceptions import CompanyAlreadyExistsError, CompanyNotFoundError
from app.models.company import Company
from app.providers.market.base import MarketDataProvider
from app.repositories.company import CompanyRepository
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyService:
    """Business operations for companies."""

    def __init__(
        self,
        company_repository: CompanyRepository,
        market_provider: MarketDataProvider,
    ) -> None:
        self.company_repository = company_repository
        self.market_provider = market_provider

    def create_company(self, company: CompanyCreate) -> Company:
        existing_company = self.company_repository.get_by_symbol(company.symbol)
        if existing_company is not None:
            raise CompanyAlreadyExistsError(company.symbol)

        return self.company_repository.create(company)

    def get_company(self, id: int) -> Company:
        company = self.company_repository.get_by_id(id)
        if company is None:
            raise CompanyNotFoundError(id)

        return company

    def get_company_by_symbol(self, symbol: str) -> Company | None:
        return self.company_repository.get_by_symbol(symbol.upper())

    def list_companies(self, skip: int = 0, limit: int = 100) -> list[Company]:
        return self.company_repository.list_companies(skip=skip, limit=limit)

    def update_company(self, id: int, updates: CompanyUpdate) -> Company:
        company = self.get_company(id)
        update_data = updates.model_dump(exclude_unset=True, mode="json")

        symbol = update_data.get("symbol")
        if symbol is not None and symbol != company.symbol:
            existing_company = self.company_repository.get_by_symbol(symbol)
            if existing_company is not None:
                raise CompanyAlreadyExistsError(symbol)

        return self.company_repository.update(company=company, updates=update_data)

    def delete_company(self, id: int) -> None:
        company = self.get_company(id)
        self.company_repository.delete(company)

    def fetch_company(self, symbol: str) -> dict[str, object]:
        """Fetch company information from the market data provider."""
        return self.market_provider.get_company(symbol)

    def fetch_quote(self, symbol: str) -> dict[str, object]:
        """Fetch the latest quote for a company."""
        return self.market_provider.get_quote(symbol)

    def search_companies(self, query: str) -> list[dict[str, object]]:
        """Search companies from the market data provider."""
        return self.market_provider.search_companies(query)

    def get_financials(self, symbol: str) -> dict[str, object]:
        """Fetch latest financial statements."""
        return self.market_provider.get_financials(symbol)

    def get_company_news(
        self,
        symbol: str,
        from_date: str,
        to_date: str,
    ) -> list[dict[str, object]]:
        """Fetch company news."""
        return self.market_provider.get_company_news(
            symbol,
            from_date,
            to_date,
        )

    def get_historical_prices(
        self,
        symbol: str,
        resolution: str,
        from_timestamp: int,
        to_timestamp: int,
    ) -> dict[str, object]:
        """Fetch historical OHLCV price data."""
        return self.market_provider.get_historical_prices(
            symbol,
            resolution,
            from_timestamp,
            to_timestamp,
        )
