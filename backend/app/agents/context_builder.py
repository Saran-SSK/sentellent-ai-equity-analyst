from __future__ import annotations

from app.services.investor_profile import InvestorProfileService
from app.services.portfolio import PortfolioService
from app.services.watchlist import WatchlistService


class ContextBuilder:
    """Builds user-specific context for AI prompts."""

    def __init__(
        self,
        investor_profile_service: InvestorProfileService,
        portfolio_service: PortfolioService,
        watchlist_service: WatchlistService,
    ) -> None:
        self.investor_profile_service = investor_profile_service
        self.portfolio_service = portfolio_service
        self.watchlist_service = watchlist_service

    def build(
        self,
        user_id: int,
        company: str | None = None,
    ) -> dict[str, str]:
        """Build user context dictionary.

        Args:
            user_id: The user's ID.
            company: Optional company symbol being analyzed.

        Returns:
            Dictionary with formatted context for investor profile, portfolio, and watchlists.
        """
        context = {
            "investor_profile": self._build_investor_profile_context(user_id),
            "portfolio": self._build_portfolio_context(user_id),
            "watchlists": self._build_watchlists_context(user_id),
        }

        return context

    def _build_investor_profile_context(self, user_id: int) -> str:
        """Build formatted investor profile context."""
        profile = self.investor_profile_service.get_profile(user_id)

        if profile is None:
            return ""

        lines = ["Investor Profile"]

        if profile.risk_profile:
            lines.append(f"Risk Profile: {profile.risk_profile}")

        if profile.investment_horizon:
            lines.append(f"Investment Horizon: {profile.investment_horizon}")

        if profile.investment_style:
            lines.append(f"Investment Style: {profile.investment_style}")

        if profile.preferred_market:
            lines.append(f"Preferred Market: {profile.preferred_market}")

        if profile.preferred_sectors:
            lines.append(f"Preferred Sectors: {profile.preferred_sectors}")

        if profile.notes:
            lines.append(f"Notes: {profile.notes}")

        return "\n".join(lines) if len(lines) > 1 else ""

    def _build_portfolio_context(self, user_id: int) -> str:
        """Build formatted portfolio context."""
        portfolios = self.portfolio_service.list_portfolios(user_id)

        if not portfolios:
            return ""

        lines = ["Current Portfolio"]

        for portfolio in portfolios:
            lines.append(f"• {portfolio.name}")
            for holding in portfolio.holdings:
                lines.append(f"  - {holding.company.symbol}")

        return "\n".join(lines)

    def _build_watchlists_context(self, user_id: int) -> str:
        """Build formatted watchlists context."""
        watchlists = self.watchlist_service.list_watchlists(user_id)

        if not watchlists:
            return ""

        lines = ["Watchlists"]

        for watchlist in watchlists:
            lines.append(watchlist.name)
            for watchlist_company in watchlist.companies:
                lines.append(f"- {watchlist_company.company.symbol}")

        return "\n".join(lines)
