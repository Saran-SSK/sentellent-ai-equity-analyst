from __future__ import annotations

from app.services.company import CompanyService


class DummyCompanyRepository:
    def __init__(self) -> None:
        self._companies = {}
        self._views = {}

    def get_by_symbol(self, symbol: str):
        return self._companies.get(symbol.upper())

    def list_companies(self, skip: int = 0, limit: int = 100):
        return list(self._companies.values())

    def create(self, company):
        self._companies[company.symbol.upper()] = company
        return company

    def track_recent_view(self, user_id: int, symbol: str):
        self._views.setdefault(user_id, []).append(symbol.upper())

    def get_recently_viewed_symbols(self, user_id: int, limit: int = 5):
        return list(reversed(self._views.get(user_id, [])[-limit:]))


class DummyMarketProvider:
    def search_companies(self, query: str):
        return []

    def get_company(self, symbol: str):
        return {
            "symbol": symbol,
            "name": f"{symbol} Corp",
            "sector": "Technology",
            "description": f"{symbol} is a leading technology company",
            "market_cap": 2_000_000_000_000,
        }

    def get_quote(self, symbol: str):
        return {
            "symbol": symbol,
            "current_price": 150.0,
            "market_cap": 2_000_000_000_000,
        }

    def get_financials(self, symbol: str):
        return {
            "symbol": symbol,
            "revenue": 500_000_000_000,
            "net_income": 60_000_000_000,
            "operating_cash_flow": 70_000_000_000,
            "free_cash_flow": 65_000_000_000,
        }

    def get_company_news(self, symbol: str, from_date: str, to_date: str):
        return [
            {
                "headline": f"{symbol} announces strong quarterly results",
                "summary": "The company posted strong growth and positive outlook.",
            }
        ]

    def get_historical_prices(
        self, symbol: str, resolution: str, from_timestamp: int, to_timestamp: int
    ):
        return {}


class DummyRecentCompanyViewRepository:
    def __init__(self, symbols: list[str]) -> None:
        self._symbols = symbols

    def get_recent_symbols(self, user_id: int, limit: int = 10):
        return self._symbols[:limit]


class TestCompanyRecommendations:
    def test_recently_viewed_company_is_ranked_first(self) -> None:
        repository = DummyCompanyRepository()
        provider = DummyMarketProvider()
        service = CompanyService(repository, provider)

        repository.track_recent_view(1, "AAPL")

        recommendations = service.get_recommendations(user_id=1, limit=3)

        assert recommendations[0]["symbol"] == "AAPL"
        assert "Recently Viewed" in recommendations[0]["why_recommended"]
        assert recommendations[0]["sentiment"] == "Positive"

    def test_get_recently_viewed_deduplicates_and_limits_results(self) -> None:
        repository = DummyCompanyRepository()
        provider = DummyMarketProvider()
        recent_repo = DummyRecentCompanyViewRepository(
            ["AAPL", "AAPL", "MSFT", "MSFT", "NVDA", "TSLA"]
        )
        service = CompanyService(
            repository,
            provider,
            recent_company_view_repository=recent_repo,
        )

        recently_viewed = service.get_recently_viewed(user_id=1, limit=3)

        assert [item["symbol"] for item in recently_viewed] == ["AAPL", "MSFT", "NVDA"]
        assert len(recently_viewed) == 3

    def test_recommendations_fill_from_live_candidates_when_history_is_short(
        self,
    ) -> None:
        repository = DummyCompanyRepository()
        provider = DummyMarketProvider()
        service = CompanyService(repository, provider)

        repository.track_recent_view(1, "AAPL")

        recommendations = service.get_recommendations(user_id=1, limit=3)

        assert len(recommendations) == 3
        assert recommendations[0]["symbol"] == "AAPL"
        assert any(item["symbol"] == "MSFT" for item in recommendations)
        assert all("Why Recommended" not in item for item in recommendations)
