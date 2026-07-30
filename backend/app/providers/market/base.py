from abc import ABC, abstractmethod


class MarketDataProvider(ABC):

    @abstractmethod
    def search_companies(self, query: str):
        pass

    @abstractmethod
    def get_company(self, symbol: str):
        pass

    @abstractmethod
    def get_quote(self, symbol: str):
        pass

    @abstractmethod
    def get_financials(self, symbol: str):
        pass