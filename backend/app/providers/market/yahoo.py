from app.clients import HttpClient
from app.core.config import settings
from app.providers.market.base import MarketDataProvider


class YahooMarketDataProvider(MarketDataProvider):
    BASE_URL = "https://finnhub.io/api/v1"

    def __init__(self, http_client: HttpClient):
        self.http = http_client
        self.api_key = settings.finnhub_api_key

    def search_companies(self, query: str):
        response = self.http.get(
            f"{self.BASE_URL}/search",
            params={
                "q": query,
                "token": self.api_key,
            },
        )

        results = []

        for company in response.get("result", []):
            results.append(
                {
                    "symbol": company.get("symbol"),
                    "name": company.get("description"),
                }
            )

        return results

    def get_company(self, symbol: str):
        response = self.http.get(
            f"{self.BASE_URL}/stock/profile2",
            params={
                "symbol": symbol,
                "token": self.api_key,
            },
        )

        return {
            "symbol": response.get("ticker"),
            "name": response.get("name"),
            "exchange": response.get("exchange"),
            "industry": response.get("finnhubIndustry"),
            "country": response.get("country"),
            "currency": response.get("currency"),
            "ipo": response.get("ipo"),
            "market_cap": response.get("marketCapitalization"),
            "logo": response.get("logo"),
            "website": response.get("weburl"),
        }

    def get_quote(self, symbol: str):
        response = self.http.get(
            f"{self.BASE_URL}/quote",
            params={
                "symbol": symbol,
                "token": self.api_key,
            },
        )

        return {
            "symbol": symbol,
            "price": response.get("c"),
            "change": response.get("d"),
            "percent_change": response.get("dp"),
            "high": response.get("h"),
            "low": response.get("l"),
            "open": response.get("o"),
            "previous_close": response.get("pc"),
        }