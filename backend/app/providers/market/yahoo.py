"""Yahoo Finance market data provider (mocked implementation).

This module provides a :class:`YahooMarketDataProvider` that implements the
:class:`MarketDataProvider` interface. It currently returns mocked/sample
data so the project can compile and be tested without real API calls or
external dependencies such as ``yfinance``.
"""

from __future__ import annotations

from typing import Any

from app.providers.market.base import MarketDataProvider


class YahooMarketDataProvider(MarketDataProvider):
    """Market data provider backed by Yahoo Finance (mocked).

    This implementation does not perform any real network requests. Instead it
    returns sample data for a small set of well-known symbols. This allows the
    rest of the application to compile and function during development and
    testing until real API integration is added.
    """

    # Sample company data keyed by symbol.
    _COMPANIES: dict[str, dict[str, Any]] = {
        "AAPL": {"symbol": "AAPL", "name": "Apple Inc."},
        "GOOGL": {"symbol": "GOOGL", "name": "Alphabet Inc."},
        "MSFT": {"symbol": "MSFT", "name": "Microsoft Corporation"},
        "AMZN": {"symbol": "AMZN", "name": "Amazon.com, Inc."},
        "TSLA": {"symbol": "TSLA", "name": "Tesla, Inc."},
    }

    # Sample quote data keyed by symbol.
    _QUOTES: dict[str, dict[str, Any]] = {
        "AAPL": {
            "symbol": "AAPL",
            "price": 175.43,
            "change": 1.23,
            "change_percent": 0.70,
            "currency": "USD",
        },
        "GOOGL": {
            "symbol": "GOOGL",
            "price": 137.89,
            "change": -0.56,
            "change_percent": -0.40,
            "currency": "USD",
        },
        "MSFT": {
            "symbol": "MSFT",
            "price": 340.21,
            "change": 2.10,
            "change_percent": 0.62,
            "currency": "USD",
        },
        "AMZN": {
            "symbol": "AMZN",
            "price": 132.55,
            "change": 1.87,
            "change_percent": 1.43,
            "currency": "USD",
        },
        "TSLA": {
            "symbol": "TSLA",
            "price": 265.12,
            "change": -3.44,
            "change_percent": -1.28,
            "currency": "USD",
        },
    }

    def get_company(self, symbol: str) -> dict[str, Any]:
        """Retrieve mocked company information for the given symbol.

        Args:
            symbol: The ticker symbol of the company (e.g. ``"AAPL"``).

        Returns:
            A dictionary containing the ``symbol`` and ``name`` of the company.
            Returns an empty dictionary if the symbol is not found.
        """
        return dict(self._COMPANIES.get(symbol.upper(), {}))

    def get_quote(self, symbol: str) -> dict[str, Any]:
        """Retrieve mocked quote data for the given symbol.

        Args:
            symbol: The ticker symbol of the company (e.g. ``"AAPL"``).

        Returns:
            A dictionary containing quote details such as ``price`` and
            ``change``. Returns an empty dictionary if the symbol is not found.
        """
        return dict(self._QUOTES.get(symbol.upper(), {}))

    def search_companies(self, query: str) -> list[dict[str, Any]]:
        """Search mocked company data for companies matching the query.

        The search is case-insensitive and matches against both the symbol
        and the company name.

        Args:
            query: The search term (e.g. ``"Apple"``).

        Returns:
            A list of dictionaries, each containing company details. Returns an
            empty list if no matches are found.
        """
        normalized_query = query.strip().lower()
        if not normalized_query:
            return []

        results: list[dict[str, Any]] = []
        for company in self._COMPANIES.values():
            if (
                normalized_query in company["symbol"].lower()
                or normalized_query in company["name"].lower()
            ):
                results.append(dict(company))
        return results
