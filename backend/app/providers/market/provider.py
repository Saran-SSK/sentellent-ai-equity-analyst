from functools import lru_cache

from app.clients import HttpClient
from app.providers.market.base import MarketDataProvider
from app.providers.market.yahoo import YahooMarketDataProvider


@lru_cache(maxsize=1)
def get_market_provider() -> MarketDataProvider:
    return YahooMarketDataProvider(HttpClient())