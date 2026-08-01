import yfinance as yf
from datetime import datetime, timedelta
from app.providers.market.base import MarketDataProvider


class YFinanceMarketDataProvider(MarketDataProvider):
    """Yahoo Finance provider using yfinance library for fallback support."""

    def search_companies(self, query: str):
        """Search for companies using Yahoo Finance."""
        try:
            # yfinance doesn't have a direct search API, so we return empty
            # This endpoint is primarily used by Finnhub
            return []
        except Exception:
            return []

    def get_company(self, symbol: str):
        """Fetch company profile from Yahoo Finance."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info:
                return None

            return {
                "symbol": symbol,
                "name": info.get("longName") or info.get("shortName", ""),
                "exchange": info.get("exchange", ""),
                "industry": info.get("industry", ""),
                "sector": info.get("sector", ""),
                "country": info.get("country", ""),
                "currency": info.get("currency", ""),
                "market_cap": info.get("marketCap"),
                "website": info.get("website", ""),
                "description": info.get("longBusinessSummary", ""),
                "employees": info.get("fullTimeEmployees"),
                "founded_year": None,  # Not available in yfinance
            }
        except Exception:
            return None

    def get_quote(self, symbol: str):
        """Fetch latest market quote from Yahoo Finance."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info:
                return None

            # Get current price from info or fast_info
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            previous_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
            
            change = None
            change_percent = None
            
            if current_price and previous_close:
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100 if previous_close != 0 else 0

            return {
                "symbol": symbol,
                "current_price": current_price,
                "change": change,
                "change_percent": change_percent,
                "open": info.get("open") or info.get("regularMarketOpen"),
                "high": info.get("dayHigh") or info.get("regularMarketDayHigh"),
                "low": info.get("dayLow") or info.get("regularMarketDayLow"),
                "volume": info.get("volume") or info.get("regularMarketVolume"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE") or info.get("forwardPE"),
                "eps": info.get("trailingEps"),
                "week_52_high": info.get("fiftyTwoWeekHigh"),
                "week_52_low": info.get("fiftyTwoWeekLow"),
            }
        except Exception:
            return None

    def get_financials(self, symbol: str):
        """Fetch latest financial statements from Yahoo Finance."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info:
                return None

            return {
                "symbol": symbol,
                "revenue": info.get("totalRevenue"),
                "net_income": info.get("netIncomeToCommon"),
                "total_assets": info.get("totalAssets"),
                "total_liabilities": info.get("totalDebt"),
                "shareholders_equity": info.get("totalStockholderEquity"),
                "operating_cash_flow": info.get("operatingCashflow"),
                "free_cash_flow": info.get("freeCashflow"),
                "year": datetime.now().year,
            }
        except Exception:
            return None

    def get_company_news(
        self,
        symbol: str,
        from_date: str,
        to_date: str,
    ):
        """Fetch company news from Yahoo Finance."""
        try:
            ticker = yf.Ticker(symbol)
            
            # Convert date strings to datetime objects
            from_dt = datetime.strptime(from_date, "%Y-%m-%d")
            to_dt = datetime.strptime(to_date, "%Y-%m-%d")
            
            # Get news from yfinance
            news = ticker.news
            
            if not news:
                return []

            filtered_news = []
            for article in news:
                pub_date = datetime.fromtimestamp(article.get("providerPublishTime", 0))
                
                # Filter by date range
                if from_dt <= pub_date <= to_dt:
                    filtered_news.append({
                        "headline": article.get("title", ""),
                        "summary": article.get("summary", ""),
                        "source": article.get("publisher", ""),
                        "url": article.get("link", ""),
                        "image": article.get("thumbnail", {}).get("resolutions", [{}])[0].get("url", "") if article.get("thumbnail") else "",
                        "published_at": article.get("providerPublishTime"),
                        "category": article.get("category", ""),
                    })

            return filtered_news
        except Exception:
            return []

    def get_historical_prices(
        self,
        symbol: str,
        resolution: str,
        from_timestamp: int,
        to_timestamp: int,
    ):
        """Fetch historical OHLCV price data from Yahoo Finance."""
        try:
            ticker = yf.Ticker(symbol)
            
            # Convert timestamps to datetime
            from_dt = datetime.fromtimestamp(from_timestamp)
            to_dt = datetime.fromtimestamp(to_timestamp)
            
            # Map resolution to yfinance interval
            interval_map = {
                "1": "1m",
                "5": "5m",
                "15": "15m",
                "30": "30m",
                "60": "1h",
                "D": "1d",
                "W": "1wk",
                "M": "1mo",
            }
            
            interval = interval_map.get(resolution, "1d")
            
            # Fetch historical data
            hist = ticker.history(start=from_dt, end=to_dt, interval=interval)
            
            if hist.empty:
                return {}

            return {
                "symbol": symbol,
                "timestamps": hist.index.strftime("%Y-%m-%d").tolist(),
                "open": hist["Open"].tolist(),
                "high": hist["High"].tolist(),
                "low": hist["Low"].tolist(),
                "close": hist["Close"].tolist(),
                "volume": hist["Volume"].tolist(),
            }
        except Exception:
            return {}
