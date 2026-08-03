from __future__ import annotations

from datetime import datetime, timedelta
import math

from sqlalchemy.exc import IntegrityError

from app.core.exceptions import CompanyAlreadyExistsError, CompanyNotFoundError
from app.models.company import Company
from app.providers.market.base import MarketDataProvider
from app.repositories.company import CompanyRepository
from app.repositories.recent_company_view import RecentCompanyViewRepository
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyService:
    """Business operations for companies."""

    def __init__(
        self,
        company_repository: CompanyRepository,
        market_provider: MarketDataProvider,
        recent_company_view_repository: RecentCompanyViewRepository | None = None,
    ) -> None:
        self.company_repository = company_repository
        self.market_provider = market_provider
        self.recent_company_view_repository = recent_company_view_repository

    def create_company(self, company: CompanyCreate) -> Company:
        existing_company = self.company_repository.get_by_symbol(company.symbol)
        if existing_company is not None:
            raise CompanyAlreadyExistsError(company.symbol)

        return self.company_repository.create(company)

    def get_company(self, id: int) -> Company:
        company = self.company_repository.get_by_id(id)
        if company is None:
            raise CompanyNotFoundError(id)

        return company

    def get_company_by_symbol(self, symbol: str) -> Company | None:
        return self.company_repository.get_by_symbol(symbol.upper())

    def get_or_create_company(self, symbol: str) -> Company:
        """Get company by symbol or create it from market data if it doesn't exist."""
        normalized_symbol = symbol.strip().upper()

        # Try to get existing company
        company = self.company_repository.get_by_symbol(normalized_symbol)
        if company is not None:
            return company

        # Fetch from market data provider
        market_data = self.market_provider.get_company(normalized_symbol)
        if not market_data:
            raise CompanyNotFoundError(
                f"Company with symbol '{normalized_symbol}' not found in market data"
            )

        # Create company from market data
        from app.schemas.company import CompanyCreate

        company_create = CompanyCreate(
            symbol=normalized_symbol,
            name=market_data.get("name", ""),
            exchange=market_data.get("exchange") or None,
            sector=market_data.get("sector") or None,
            industry=market_data.get("industry") or None,
            country=market_data.get("country") or None,
            currency=market_data.get("currency") or None,
            description=market_data.get("description") or None,
            website=market_data.get("website") or None,
        )

        try:
            return self.company_repository.create(company_create)
        except IntegrityError:
            # Race condition: another request inserted the company
            # Roll back the session and re-query
            self.company_repository.session.rollback()
            company = self.company_repository.get_by_symbol(normalized_symbol)
            if company is not None:
                return company
            # If still not found after rollback, raise the original error
            raise

    def list_companies(self, skip: int = 0, limit: int = 100) -> list[Company]:
        return self.company_repository.list_companies(skip=skip, limit=limit)

    def update_company(self, id: int, updates: CompanyUpdate) -> Company:
        company = self.get_company(id)
        update_data = updates.model_dump(exclude_unset=True, mode="json")

        symbol = update_data.get("symbol")
        if symbol is not None and symbol != company.symbol:
            existing_company = self.company_repository.get_by_symbol(symbol)
            if existing_company is not None:
                raise CompanyAlreadyExistsError(symbol)

        return self.company_repository.update(company=company, updates=update_data)

    def delete_company(self, id: int) -> None:
        company = self.get_company(id)
        self.company_repository.delete(company)

    def fetch_company(self, symbol: str) -> dict[str, object]:
        """Fetch company information from the market data provider with database id."""
        # Ensure company exists in database
        company = self.get_or_create_company(symbol)

        # Fetch market data
        market_data = self.market_provider.get_company(symbol)
        if not market_data:
            return {"id": company.id, "symbol": symbol, "name": company.name}

        # Add database id to market data
        market_data["id"] = company.id
        return market_data

    def fetch_quote(self, symbol: str) -> dict[str, object]:
        """Fetch the latest quote for a company."""
        return self.market_provider.get_quote(symbol)

    def search_companies(self, query: str) -> list[dict[str, object]]:
        """Search companies from the market data provider."""
        return self.market_provider.search_companies(query)

    def get_financials(self, symbol: str) -> dict[str, object]:
        """Fetch latest financial statements."""
        return self.market_provider.get_financials(symbol)

    def get_company_news(
        self,
        symbol: str,
        from_date: str,
        to_date: str,
    ) -> list[dict[str, object]]:
        """Fetch company news."""
        return self.market_provider.get_company_news(
            symbol,
            from_date,
            to_date,
        )

    def get_historical_prices(
        self,
        symbol: str,
        resolution: str,
        from_timestamp: int,
        to_timestamp: int,
    ) -> dict[str, object]:
        """Fetch historical OHLCV price data."""
        return self.market_provider.get_historical_prices(
            symbol,
            resolution,
            from_timestamp,
            to_timestamp,
        )

    def track_recent_view(self, user_id: int, symbol: str) -> None:
        """Persist a user's recently viewed company."""
        if self.recent_company_view_repository is not None:
            self.recent_company_view_repository.add_view(user_id, symbol)
            return

        if hasattr(self.company_repository, "track_recent_view"):
            self.company_repository.track_recent_view(user_id, symbol)

    def get_recently_viewed(
        self, user_id: int, limit: int = 5
    ) -> list[dict[str, object]]:
        """Get recently viewed companies for a user, ordered by most recent view."""
        recent_symbols = []
        if self.recent_company_view_repository is not None:
            recent_symbols = self.recent_company_view_repository.get_recent_symbols(
                user_id,
                limit=limit,
            )
        elif hasattr(self.company_repository, "get_recently_viewed_symbols"):
            recent_symbols = self.company_repository.get_recently_viewed_symbols(
                user_id,
                limit=limit,
            )

        recently_viewed = []
        seen_symbols: set[str] = set()
        for symbol in recent_symbols[: limit * 3]:
            # Normalize symbol: uppercase and remove exchange suffixes
            normalized_symbol = symbol.upper().replace(".NS", "").replace(".BO", "")
            if normalized_symbol in seen_symbols:
                continue
            seen_symbols.add(normalized_symbol)

            profile = self.market_provider.get_company(normalized_symbol) or {}
            news_items = (
                self.market_provider.get_company_news(
                    normalized_symbol,
                    (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                    datetime.now().strftime("%Y-%m-%d"),
                )
                or []
            )
            sentiment = self._get_news_sentiment(news_items)

            recently_viewed.append(
                {
                    "symbol": normalized_symbol,
                    "name": profile.get("name") or normalized_symbol,
                    "sector": profile.get("sector") or "Unknown",
                    "sentiment": sentiment.capitalize(),
                }
            )

            if len(recently_viewed) >= limit:
                break

        return recently_viewed

    def get_recommendations(
        self, user_id: int, limit: int = 6
    ) -> list[dict[str, object]]:
        """Generate personalized company recommendations for a user.

        Recommendations are based on:
        - Market Capitalization
        - Strong Fundamentals
        - Strong Cash Flow
        - Positive News Sentiment
        - Revenue Growth
        - Profitability

        Only Indian companies (NSE/BSE) are recommended.
        """
        # Get Indian-only candidate symbols
        indian_candidates = self._get_indian_candidate_symbols(
            limit * 10
        )  # Get more candidates to filter

        print(f"Total Indian candidates: {len(indian_candidates)}")

        ranked: list[dict[str, object]] = []
        seen_symbols: set[str] = set()

        for symbol in indian_candidates:
            if symbol in seen_symbols:
                continue
            seen_symbols.add(symbol)

            try:
                recommendation = self._build_recommendation(symbol, is_recent=False)
                ranked.append(recommendation)
                print(
                    f"Built recommendation for {symbol}: score={recommendation['score']}"
                )
            except Exception as e:
                print(f"Error building recommendation for {symbol}: {e}")
                continue

        print(f"Total recommendations built: {len(ranked)}")
        ranked.sort(key=lambda item: item["score"], reverse=True)
        print(f"Top {limit} recommendations: {[r['symbol'] for r in ranked[:limit]]}")
        return ranked[:limit]

    def _get_indian_candidate_symbols(self, count: int) -> list[str]:
        """Get Indian company symbols (NSE/BSE) for recommendations."""
        # Try to get from database first
        companies = self.company_repository.list_companies(skip=0, limit=200)
        if companies:
            # Filter for Indian companies (those with .NS or .BO suffix, or known Indian symbols)
            indian_symbols = []
            for company in companies:
                if not company.symbol:
                    continue
                symbol = company.symbol.upper()
                # Include if it has Indian exchange suffix or is in our known Indian list
                if symbol.endswith(".NS") or symbol.endswith(".BO"):
                    indian_symbols.append(symbol.replace(".NS", "").replace(".BO", ""))
                # Also include known Indian companies without suffix
                elif symbol in self._get_known_indian_symbols():
                    indian_symbols.append(symbol)

            if len(indian_symbols) >= count:
                return indian_symbols[:count]
            if indian_symbols:
                return indian_symbols

        # Fallback to known Indian companies
        return self._get_known_indian_symbols()[:count]

    def _get_known_indian_symbols(self) -> list[str]:
        """Return comprehensive list of Indian company symbols (NSE/BSE)."""
        return [
            # IT Services
            "TCS",
            "INFY",
            "WIPRO",
            "HCLTECH",
            "LTIM",
            "TECHM",
            "MPHASIS",
            "LTI",
            "PERSISTENT",
            "ZENSAR",
            # Banking - Private
            "HDFCBANK",
            "ICICIBANK",
            "KOTAKBANK",
            "AXISBANK",
            "INDUSINDBK",
            "IDFCFIRSTB",
            "FEDERALBNK",
            "RBLBANK",
            # Banking - PSU
            "SBIN",
            "PNB",
            "BANKBARODA",
            "CANBK",
            "UNIONBANK",
            "MAHABANK",
            "INDIANB",
            # Financial Services
            "BAJFINANCE",
            "BAJAJFINSV",
            "CHOLAFIN",
            "MUTHOOTFIN",
            "MANAPPURAM",
            "TATASTEEL",
            "TATAMOTORS",
            # Insurance
            "ICICIGI",
            "HDFCLIFE",
            "SBILIFE",
            "MAXFIN",
            "ICICIPRULI",
            # Oil & Gas
            "RELIANCE",
            "ONGC",
            "OIL",
            "GAIL",
            "IOC",
            "BPCL",
            "HPCL",
            # Power
            "NTPC",
            "POWERGRID",
            "TATAPOWER",
            "ADANIPORTS",
            "ADANIGREEN",
            "ADANITRANS",
            "JSWENERGY",
            # Metals
            "TATASTEEL",
            "JSWSTEEL",
            "HINDALCO",
            "NMDC",
            "COALINDIA",
            # Infrastructure
            "LT",
            "DLF",
            "GODREJPROP",
            "BRIGADE",
            "OBEROIRLTY",
            # Consumer Durables
            "TITAN",
            "WHIRLPOOL",
            "BLUESTAR",
            "HAVELLS",
            "VOLTAS",
            # FMCG
            "ITC",
            "HINDUNILVR",
            "NESTLEIND",
            "BRITANNIA",
            "HINDUSTANUNILEVER",
            "GILLETTE",
            "PGHH",
            # Automobile
            "MARUTI",
            "TATAMOTORS",
            "M&M",
            "BAJAJ-AUTO",
            "EICHERMOT",
            "HEROMOTOCO",
            # Pharma
            "SUNPHARMA",
            "DRREDDY",
            "CIPLA",
            "AUROPHARMA",
            "LUPIN",
            "DIVISLAB",
            "ZYDUSLIFE",
            "TORNTPHARM",
            # Telecom
            "BHARTIARTL",
            "VODAFONEIDEA",
            "MTNL",
            # Chemicals
            "UPL",
            "PIIND",
            "SRF",
            "NAVINFLUOR",
            "DEEPAKNTR",
            # Cement
            "ULTRACEMCO",
            "ACC",
            "AMBUJACEM",
            "DalmiaBhar",
            "SHREECEM",
            "RAMCOCEM",
            # Retail
            "DMART",
            "TRENT",
            "FUTURECONSUMER",
            "V-MART",
            # Real Estate
            "DLF",
            "GODREJPROP",
            "BRIGADE",
            "OBEROIRLTY",
            "PHOENIXLTD",
            # Logistics
            "CONCOR",
            "GATI",
            "ALLCARGO",
            # Media
            "ZEEENT",
            "SUNTV",
            "PVRINOX",
            "INOXLEISUR",
            # Textiles
            "ARVIND",
            "WELSPUNLIV",
            "TRIDENT",
            # Others
            "ADANIENT",
            "ADANIPORTS",
            "ADANIGREEN",
            "ADANITRANS",
            "ADANIPOWER",
            "TATACONSUM",
            "TATACOMM",
            "TATASTEEL",
            "TATAMOTORS",
            "GODREJCP",
            "GODREJIND",
            "GODREJPROP",
            "MAHINDRA",
            "MASTEEL",
            "M&MFIN",
        ]

    def _get_live_candidate_symbols(self, count: int) -> list[str]:
        companies = self.company_repository.list_companies(skip=0, limit=200)
        if companies:
            symbols = [company.symbol for company in companies if company.symbol]
            if len(symbols) >= count:
                return symbols[:count]
            return symbols

        fallback_symbols = [
            "AAPL",
            "MSFT",
            "NVDA",
            "GOOGL",
            "TSLA",
            "AMZN",
            "META",
            "NFLX",
        ]
        return fallback_symbols[:count]

    def _build_recommendation(
        self,
        symbol: str,
        *,
        is_recent: bool = False,
    ) -> dict[str, object]:
        profile = self.market_provider.get_company(symbol) or {}
        quote = self.market_provider.get_quote(symbol) or {}
        financials = self.market_provider.get_financials(symbol) or {}
        news_items = (
            self.market_provider.get_company_news(
                symbol,
                (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                datetime.now().strftime("%Y-%m-%d"),
            )
            or []
        )

        price = quote.get("current_price")
        market_cap = profile.get("market_cap") or quote.get("market_cap")
        revenue = financials.get("revenue")
        net_income = financials.get("net_income")
        cash_flow = financials.get("operating_cash_flow") or financials.get(
            "free_cash_flow"
        )
        sentiment = self._get_news_sentiment(news_items)

        score = 0.0
        why_recommended: list[str] = []

        # Market Cap scoring
        if market_cap:
            if market_cap >= 2_000_000_000_000:
                score += 18.0
                why_recommended.append("Large Market Cap")
            elif market_cap >= 300_000_000_000:
                score += 10.0

        # Fundamentals scoring (profitability)
        if revenue and net_income:
            if net_income > 0 and revenue > 0:
                margin = (net_income / revenue) * 100
                if margin >= 12:
                    score += 16.0
                    why_recommended.append("Strong Fundamentals")
                elif margin >= 5:
                    score += 8.0

        # Cash Flow scoring
        if cash_flow and cash_flow > 0:
            if cash_flow >= 10_000_000_000:
                score += 10.0
                why_recommended.append("Strong Cash Flow")
            elif cash_flow >= 1_000_000_000:
                score += 5.0

        # Valuation scoring
        if price and market_cap and market_cap > 0:
            valuation = market_cap / max(price, 1)
            if valuation < 2_000_000_000_000 / 100 and price > 0:
                score += 8.0
                why_recommended.append("Attractive Valuation")

        # News sentiment scoring
        if sentiment == "Positive":
            score += 12.0
            why_recommended.append("Positive News")
        elif sentiment == "Neutral":
            score += 2.0

        if not why_recommended:
            why_recommended = ["Strong Fundamentals"]

        # Shorten description to 2-3 lines
        full_description = (
            profile.get("description")
            or profile.get("industry")
            or "High-potential company"
        )
        short_description = self._shorten_description(full_description)

        return {
            "symbol": symbol.upper(),
            "name": profile.get("name") or symbol.upper(),
            "description": short_description,
            "current_price": price,
            "market_cap": market_cap,
            "sector": profile.get("sector") or "Unknown",
            "sentiment": sentiment,
            "why_recommended": why_recommended,
            "score": round(score, 2),
        }

    def _shorten_description(self, description: str, max_length: int = 150) -> str:
        """Shorten description to 2-3 lines (approximately 150 characters)."""
        if not description:
            return "High-potential company"

        # Remove extra whitespace
        description = " ".join(description.split())

        # Truncate if too long
        if len(description) <= max_length:
            return description

        # Find last complete word within limit
        truncated = description[:max_length]
        last_space = truncated.rfind(" ")
        if last_space > 0:
            truncated = truncated[:last_space]

        return truncated + "..."

    def _get_news_sentiment(self, news_items: list[dict[str, object]]) -> str:
        if not news_items:
            return "Neutral"

        positive_keywords = {
            "positive",
            "strong",
            "growth",
            "beat",
            "surge",
            "gains",
            "outperform",
        }
        negative_keywords = {
            "negative",
            "weak",
            "decline",
            "down",
            "cut",
            "loss",
            "miss",
        }

        positive_count = 0
        negative_count = 0

        for item in news_items:
            text = " ".join(
                [str(item.get("headline", "")), str(item.get("summary", ""))]
            ).lower()
            if any(keyword in text for keyword in positive_keywords):
                positive_count += 1
            if any(keyword in text for keyword in negative_keywords):
                negative_count += 1

        if positive_count > negative_count:
            return "Positive"
        if negative_count > positive_count:
            return "Negative"
        return "Neutral"
