from __future__ import annotations

import requests

from app.core.config import settings


class FinnhubProvider:
    """Provider for interacting with the Finnhub API."""

    BASE_URL = "https://finnhub.io/api/v1"

    def get_company_news(
        self,
        symbol: str,
        from_date: str,
        to_date: str,
    ) -> list[dict]:
        """Fetch company news for a given symbol."""

        response = requests.get(
            f"{self.BASE_URL}/company-news",
            params={
                "symbol": symbol,
                "from": from_date,
                "to": to_date,
                "token": settings.finnhub_api_key,
            },
            timeout=30,
        )

        response.raise_for_status()

        return response.json()


finnhub_provider = FinnhubProvider()
