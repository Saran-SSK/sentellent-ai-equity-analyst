"""Market data provider abstraction layer.

This package provides a unified interface for retrieving market data from
different providers. Each provider implements the :class:`MarketDataProvider`
abstract base class and can be accessed through the :func:`get_market_provider`
factory function.
"""

from app.providers.market.base import MarketDataProvider
from app.providers.market.yahoo import YahooMarketDataProvider
from app.providers.market.provider import get_market_provider

__all__ = [
    "MarketDataProvider",
    "YahooMarketDataProvider",
    "get_market_provider",
]
