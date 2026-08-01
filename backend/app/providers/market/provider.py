from functools import lru_cache

from app.clients import HttpClient
from app.providers.market.base import MarketDataProvider
from app.providers.market.hybrid import HybridMarketDataProvider


@lru_cache(maxsize=1)
def get_market_provider() -> MarketDataProvider:
    return HybridMarketDataProvider(HttpClient())