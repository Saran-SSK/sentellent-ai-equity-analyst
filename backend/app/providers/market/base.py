"""Abstract base class for market data providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class MarketDataProvider(ABC):
    """Abstract base class defining the market data provider interface.

    All concrete market data providers must implement the methods defined
    here so that services can interact with them in a provider-agnostic way.
    """

    @abstractmethod
    def get_company(self, symbol: str) -> dict[str, Any]:
        """Retrieve basic company information for the given symbol.

        Args:
            symbol: The ticker symbol of the company (e.g. ``"AAPL"``).

        Returns:
            A dictionary containing company details such as ``symbol`` and
            ``name``.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError

    @abstractmethod
    def get_quote(self, symbol: str) -> dict[str, Any]:
        """Retrieve the latest quote for the given symbol.

        Args:
            symbol: The ticker symbol of the company (e.g. ``"AAPL"``).

        Returns:
            A dictionary containing quote details such as ``symbol``,
            ``price``, and ``change``.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError

    @abstractmethod
    def search_companies(self, query: str) -> list[dict[str, Any]]:
        """Search for companies matching the given query string.

        Args:
            query: The search term (e.g. ``"Apple"``).

        Returns:
            A list of dictionaries, each containing company details such as
            ``symbol`` and ``name``.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError
