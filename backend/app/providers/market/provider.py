"""Factory for obtaining the active market data provider.

This module provides a singleton factory function :func:`get_market_provider`
that returns the currently configured :class:`MarketDataProvider` instance.
By routing all provider access through this factory, the rest of the
application remains decoupled from any specific provider implementation and
can switch providers simply by changing the factory.
"""

from __future__ import annotations

from functools import lru_cache

from app.providers.market.base import MarketDataProvider
from app.providers.market.yahoo import YahooMarketDataProvider


@lru_cache(maxsize=1)
def get_market_provider() -> MarketDataProvider:
    """Return the singleton market data provider instance.

    The provider is cached using :func:`functools.lru_cache` so that repeated
    calls return the same instance. To switch providers, update this function
    (or invalidate the cache) rather than modifying service code.

    Returns:
        An instance of the active :class:`MarketDataProvider` implementation.
    """
    return YahooMarketDataProvider()
