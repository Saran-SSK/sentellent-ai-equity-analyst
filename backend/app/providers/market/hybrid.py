import logging
from app.clients import HttpClient
from app.core.config import settings
from app.providers.market.base import MarketDataProvider
from app.providers.market.yahoo import YahooMarketDataProvider
from app.providers.market.yfinance_provider import YFinanceMarketDataProvider

logger = logging.getLogger(__name__)


class HybridMarketDataProvider(MarketDataProvider):
    """
    Hybrid market data provider that uses Finnhub as primary and yfinance as fallback.
    
    Provider Mapping:
    - search_companies: Finnhub only (no fallback)
    - get_company: Finnhub -> yfinance fallback on 403/error
    - get_quote: Finnhub -> yfinance fallback on 403/error
    - get_financials: Finnhub -> yfinance fallback on 403/error
    - get_company_news: Finnhub -> yfinance fallback on 403/error
    - get_historical_prices: Alpha Vantage (via Finnhub provider) -> yfinance fallback on 403/error
    """

    def __init__(self, http_client: HttpClient):
        self.http = http_client
        self.finnhub_provider = YahooMarketDataProvider(http_client)
        self.yfinance_provider = YFinanceMarketDataProvider()

    def search_companies(self, query: str):
        """Search companies using Finnhub only (no fallback)."""
        try:
            return self.finnhub_provider.search_companies(query)
        except Exception as e:
            logger.error(f"Error in search_companies: {e}")
            return []

    def get_company(self, symbol: str):
        """Fetch company profile with Finnhub -> yfinance fallback."""
        try:
            result = self.finnhub_provider.get_company(symbol)
            if result:
                logger.info(f"Successfully fetched company profile for {symbol} from Finnhub")
                return result
        except Exception as e:
            logger.warning(f"Finnhub failed for company profile {symbol}: {e}, trying yfinance fallback")
        
        # Fallback to yfinance
        try:
            result = self.yfinance_provider.get_company(symbol)
            if result:
                logger.info(f"Successfully fetched company profile for {symbol} from yfinance fallback")
                return result
        except Exception as e:
            logger.error(f"yfinance fallback failed for company profile {symbol}: {e}")
        
        return None

    def get_quote(self, symbol: str):
        """Fetch quote with Finnhub -> yfinance fallback."""
        try:
            result = self.finnhub_provider.get_quote(symbol)
            if result:
                logger.info(f"Successfully fetched quote for {symbol} from Finnhub")
                return result
        except Exception as e:
            logger.warning(f"Finnhub failed for quote {symbol}: {e}, trying yfinance fallback")
        
        # Fallback to yfinance
        try:
            result = self.yfinance_provider.get_quote(symbol)
            if result:
                logger.info(f"Successfully fetched quote for {symbol} from yfinance fallback")
                return result
        except Exception as e:
            logger.error(f"yfinance fallback failed for quote {symbol}: {e}")
        
        return None

    def get_financials(self, symbol: str):
        """Fetch financials with Finnhub -> yfinance fallback."""
        try:
            result = self.finnhub_provider.get_financials(symbol)
            if result:
                logger.info(f"Successfully fetched financials for {symbol} from Finnhub")
                return result
        except Exception as e:
            logger.warning(f"Finnhub failed for financials {symbol}: {e}, trying yfinance fallback")
        
        # Fallback to yfinance
        try:
            result = self.yfinance_provider.get_financials(symbol)
            if result:
                logger.info(f"Successfully fetched financials for {symbol} from yfinance fallback")
                return result
        except Exception as e:
            logger.error(f"yfinance fallback failed for financials {symbol}: {e}")
        
        return None

    def get_company_news(
        self,
        symbol: str,
        from_date: str,
        to_date: str,
    ):
        """Fetch company news with Finnhub -> yfinance fallback."""
        try:
            result = self.finnhub_provider.get_company_news(symbol, from_date, to_date)
            if result:
                logger.info(f"Successfully fetched news for {symbol} from Finnhub")
                return result
        except Exception as e:
            logger.warning(f"Finnhub failed for news {symbol}: {e}, trying yfinance fallback")
        
        # Fallback to yfinance
        try:
            result = self.yfinance_provider.get_company_news(symbol, from_date, to_date)
            if result:
                logger.info(f"Successfully fetched news for {symbol} from yfinance fallback")
                return result
        except Exception as e:
            logger.error(f"yfinance fallback failed for news {symbol}: {e}")
        
        return []

    def get_historical_prices(
        self,
        symbol: str,
        resolution: str,
        from_timestamp: int,
        to_timestamp: int,
    ):
        """Fetch historical prices with Alpha Vantage (via Finnhub) -> yfinance fallback."""
        try:
            result = self.finnhub_provider.get_historical_prices(symbol, resolution, from_timestamp, to_timestamp)
            if result:
                logger.info(f"Successfully fetched historical prices for {symbol} from Alpha Vantage")
                return result
        except Exception as e:
            logger.warning(f"Alpha Vantage failed for historical prices {symbol}: {e}, trying yfinance fallback")
        
        # Fallback to yfinance
        try:
            result = self.yfinance_provider.get_historical_prices(symbol, resolution, from_timestamp, to_timestamp)
            if result:
                logger.info(f"Successfully fetched historical prices for {symbol} from yfinance fallback")
                return result
        except Exception as e:
            logger.error(f"yfinance fallback failed for historical prices {symbol}: {e}")
        
        return {}
