from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.services.company import CompanyService


class LiveDataRetrievalService:
    """Service for fetching live company data when RAG documents are unavailable."""

    def __init__(self, company_service: CompanyService) -> None:
        self.company_service = company_service

    def fetch_live_company_data(
        self,
        company: str,
    ) -> dict[str, Any]:
        """Fetch live company data from market providers.

        Args:
            company: Company symbol

        Returns:
            Dictionary with live company data including profile, quote, fundamentals, and news
        """
        try:
            # Fetch company profile
            profile = self.company_service.fetch_company(company)
            
            # Fetch quote
            quote = self.company_service.fetch_quote(company)
            
            # Fetch financials
            financials = self.company_service.get_financials(company)
            
            # Fetch latest news (last 30 days, same as Company Details page)
            to_date = datetime.now()
            from_date = to_date - timedelta(days=30)
            news = self.company_service.get_company_news(
                company,
                from_date.strftime("%Y-%m-%d"),
                to_date.strftime("%Y-%m-%d"),
            )
            
            # Build context from live data
            context_parts = []
            
            # Add profile information
            if profile:
                profile_text = self._build_profile_context(profile)
                context_parts.append(profile_text)
            
            # Add quote information
            if quote:
                quote_text = self._build_quote_context(quote)
                context_parts.append(quote_text)
            
            # Add financials information
            if financials:
                financials_text = self._build_financials_context(financials)
                context_parts.append(financials_text)
            
            # Add news information
            if news:
                news_text = self._build_news_context(news)
                context_parts.append(news_text)
            
            return {
                "context": "\n\n".join(context_parts),
                "source": "live_market_data",
                "has_data": len(context_parts) > 0,
            }
        except Exception as e:
            # Log error but don't fail - RAG may still work
            print(f"Error fetching live data for {company}: {e}")
            return {
                "context": "",
                "source": "live_market_data",
                "has_data": False,
            }

    def _build_profile_context(self, profile: dict[str, Any]) -> str:
        """Build context from company profile."""
        lines = ["Company Profile"]
        
        if profile.get("name"):
            lines.append(f"Name: {profile['name']}")
        if profile.get("symbol"):
            lines.append(f"Symbol: {profile['symbol']}")
        if profile.get("exchange"):
            lines.append(f"Exchange: {profile['exchange']}")
        if profile.get("sector"):
            lines.append(f"Sector: {profile['sector']}")
        if profile.get("industry"):
            lines.append(f"Industry: {profile['industry']}")
        if profile.get("country"):
            lines.append(f"Country: {profile['country']}")
        if profile.get("description"):
            lines.append(f"Description: {profile['description']}")
        if profile.get("website"):
            lines.append(f"Website: {profile['website']}")
        if profile.get("market_cap"):
            lines.append(f"Market Cap: {profile['market_cap']}")
        if profile.get("employees"):
            lines.append(f"Employees: {profile['employees']}")
        
        return "\n".join(lines)

    def _build_quote_context(self, quote: dict[str, Any]) -> str:
        """Build context from market quote."""
        lines = ["Current Market Data"]
        
        if quote.get("current_price"):
            lines.append(f"Current Price: {quote['current_price']}")
        if quote.get("change") is not None:
            lines.append(f"Change: {quote['change']}")
        if quote.get("change_percent") is not None:
            lines.append(f"Change %: {quote['change_percent']:.2f}%")
        if quote.get("open"):
            lines.append(f"Open: {quote['open']}")
        if quote.get("high"):
            lines.append(f"Day High: {quote['high']}")
        if quote.get("low"):
            lines.append(f"Day Low: {quote['low']}")
        if quote.get("volume"):
            lines.append(f"Volume: {quote['volume']}")
        if quote.get("market_cap"):
            lines.append(f"Market Cap: {quote['market_cap']}")
        if quote.get("pe_ratio"):
            lines.append(f"P/E Ratio: {quote['pe_ratio']}")
        if quote.get("eps"):
            lines.append(f"EPS: {quote['eps']}")
        if quote.get("week_52_high"):
            lines.append(f"52 Week High: {quote['week_52_high']}")
        if quote.get("week_52_low"):
            lines.append(f"52 Week Low: {quote['week_52_low']}")
        
        return "\n".join(lines)

    def _build_financials_context(self, financials: dict[str, Any]) -> str:
        """Build context from financial statements."""
        lines = ["Financial Statements"]
        
        if financials.get("year"):
            lines.append(f"Fiscal Year: {financials['year']}")
        if financials.get("revenue"):
            lines.append(f"Revenue: {financials['revenue']}")
        if financials.get("net_income"):
            lines.append(f"Net Income: {financials['net_income']}")
        if financials.get("total_assets"):
            lines.append(f"Total Assets: {financials['total_assets']}")
        if financials.get("total_liabilities"):
            lines.append(f"Total Liabilities: {financials['total_liabilities']}")
        if financials.get("shareholders_equity"):
            lines.append(f"Shareholders Equity: {financials['shareholders_equity']}")
        if financials.get("operating_cash_flow"):
            lines.append(f"Operating Cash Flow: {financials['operating_cash_flow']}")
        if financials.get("free_cash_flow"):
            lines.append(f"Free Cash Flow: {financials['free_cash_flow']}")
        
        return "\n".join(lines)

    def _build_news_context(self, news: list[dict[str, Any]]) -> str:
        """Build context from company news."""
        lines = ["Recent News"]
        
        for article in news[:10]:  # Limit to 10 most recent articles
            headline = article.get("headline", "")
            summary = article.get("summary", "")
            source = article.get("source", "")
            published_at = article.get("published_at", "")
            
            if headline:
                lines.append(f"Headline: {headline}")
            if summary:
                lines.append(f"Summary: {summary}")
            if source:
                lines.append(f"Source: {source}")
            if published_at:
                lines.append(f"Published: {published_at}")
            lines.append("")  # Empty line between articles
        
        return "\n".join(lines)
