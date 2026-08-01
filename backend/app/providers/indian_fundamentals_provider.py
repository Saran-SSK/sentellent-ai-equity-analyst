from __future__ import annotations

import logging
from typing import Any

import yfinance as yf

logger = logging.getLogger(__name__)


class IndianFundamentalsProvider:
    """Provider for fetching fundamentals data for Indian NSE/BSE companies using yfinance."""

    def __init__(self) -> None:
        pass

    def get_fundamentals(self, company: str) -> dict[str, Any]:
        """Fetch fundamentals data for an Indian company.

        Args:
            company: Company ticker symbol (e.g., "TCS", "RELIANCE", "INFY")

        Returns:
            Dictionary containing available fundamentals fields:
            - company
            - resolved_ticker (the actual yfinance symbol used)
            - current_price
            - market_cap
            - pe_ratio
            - pb_ratio
            - eps
            - roe (normalized to percentage)
            - dividend_yield (normalized to percentage)
            - debt_to_equity
            - book_value
            - fifty_two_week_high
            - fifty_two_week_low
            - sector
            - industry
            - business_summary

        Raises:
            ValueError: If company ticker is empty or invalid
        """
        if not company or not company.strip():
            raise ValueError("Company ticker cannot be empty")

        company_stripped = company.strip().upper()

        # Try .NS first, then .BO as fallback
        yfinance_symbols = []
        if company_stripped.endswith(".NS"):
            yfinance_symbols.append(company_stripped)
        elif company_stripped.endswith(".BO"):
            yfinance_symbols.append(company_stripped)
        else:
            yfinance_symbols.append(f"{company_stripped}.NS")
            yfinance_symbols.append(f"{company_stripped}.BO")

        resolved_ticker = None
        last_error = None

        for yfinance_symbol in yfinance_symbols:
            try:
                logger.debug(f"Attempting to fetch fundamentals for {yfinance_symbol}")
                ticker = yf.Ticker(yfinance_symbol)
                info = ticker.info

                if not info:
                    logger.debug(f"No info data for {yfinance_symbol}")
                    continue

                resolved_ticker = yfinance_symbol
                break
            except Exception as e:
                logger.debug(f"Failed to fetch {yfinance_symbol}: {e}")
                last_error = e
                continue

        if not resolved_ticker:
            raise ValueError(
                f"Invalid ticker or no data available for company: {company}. "
                f"Tried: {', '.join(yfinance_symbols)}"
            ) from last_error

        ticker = yf.Ticker(resolved_ticker)
        info = ticker.info
        fast_info = ticker.fast_info if hasattr(ticker, "fast_info") else None

        logger.info(f"Successfully fetched fundamentals for {company} using {resolved_ticker}")

        # Build result with only available fields
        result = {
            "company": company_stripped,
            "resolved_ticker": resolved_ticker,
        }

        # Current price - try fast_info first
        current_price = None
        if fast_info and fast_info.get("last_price") is not None:
            current_price = fast_info.get("last_price")
        else:
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        if current_price is not None:
            result["current_price"] = current_price

        # Market cap - try fast_info first
        market_cap = None
        if fast_info and fast_info.get("market_cap") is not None:
            market_cap = fast_info.get("market_cap")
        else:
            market_cap = info.get("marketCap")
        if market_cap is not None:
            result["market_cap"] = market_cap

        # P/E ratio
        pe_ratio = info.get("trailingPE") or info.get("forwardPE")
        if pe_ratio is not None:
            result["pe_ratio"] = pe_ratio

        # P/B ratio
        pb_ratio = info.get("priceToBook")
        if pb_ratio is not None:
            result["pb_ratio"] = pb_ratio

        # EPS
        eps = info.get("trailingEps")
        if eps is not None:
            result["eps"] = eps

        # ROE - normalize to percentage
        roe = info.get("returnOnEquity")
        if roe is not None:
            result["roe"] = roe * 100 if roe < 1 else roe

        # Dividend yield - normalize to percentage
        dividend_yield = info.get("dividendYield")
        if dividend_yield is not None:
            result["dividend_yield"] = dividend_yield * 100 if dividend_yield < 1 else dividend_yield

        # Debt to equity
        debt_to_equity = info.get("debtToEquity")
        if debt_to_equity is not None:
            result["debt_to_equity"] = debt_to_equity

        # Book value
        book_value = info.get("bookValue")
        if book_value is not None:
            result["book_value"] = book_value

        # 52-week high - try fast_info first
        fifty_two_week_high = None
        if fast_info and fast_info.get("year_high") is not None:
            fifty_two_week_high = fast_info.get("year_high")
        else:
            fifty_two_week_high = info.get("fiftyTwoWeekHigh")
        if fifty_two_week_high is not None:
            result["fifty_two_week_high"] = fifty_two_week_high

        # 52-week low - try fast_info first
        fifty_two_week_low = None
        if fast_info and fast_info.get("year_low") is not None:
            fifty_two_week_low = fast_info.get("year_low")
        else:
            fifty_two_week_low = info.get("fiftyTwoWeekLow")
        if fifty_two_week_low is not None:
            result["fifty_two_week_low"] = fifty_two_week_low

        # Sector
        sector = info.get("sector")
        if sector:
            result["sector"] = sector

        # Industry
        industry = info.get("industry")
        if industry:
            result["industry"] = industry

        # Business summary
        business_summary = info.get("longBusinessSummary")
        if business_summary:
            result["business_summary"] = business_summary

        return result


indian_fundamentals_provider = IndianFundamentalsProvider()
