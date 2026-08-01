from __future__ import annotations

from typing import Any

from langchain_core.documents import Document

from app.ingestion.text_splitter import text_splitter
from app.ingestion.company_ingestion import company_ingestion_service
from app.providers.indian_fundamentals_provider import indian_fundamentals_provider


class FundamentalsIngestionService:
    """Service for ingesting company fundamentals into the document store."""

    def ingest_fundamentals(self, company: str) -> dict[str, Any]:
        """Fetch fundamentals for a company and ingest them into Qdrant.

        Args:
            company: Company ticker symbol (e.g., "TCS", "RELIANCE", "INFY")

        Returns:
            Dictionary with ingestion results:
            - company
            - chunks_created
            - status

        Raises:
            ValueError: If company is empty or fundamentals cannot be fetched
        """
        if not company or not company.strip():
            raise ValueError("Company is required for fundamentals ingestion.")

        company_stripped = company.strip().upper()

        # Fetch fundamentals using the IndianFundamentalsProvider
        fundamentals = indian_fundamentals_provider.get_fundamentals(company_stripped)

        # Convert structured data to natural-language document
        document_text = self._build_document_text(fundamentals)

        # Build metadata
        metadata = self._build_metadata(fundamentals)

        # Create LangChain Document
        document = Document(page_content=document_text, metadata=metadata)

        # Split document into chunks
        split_documents = text_splitter.split([document])

        # Extract chunk texts
        chunk_texts = [
            chunk.page_content.strip()
            for chunk in split_documents
            if chunk.page_content and chunk.page_content.strip()
        ]

        # Build chunk metadata
        chunk_metadata = [
            {
                **(chunk.metadata or {}),
                "company": company_stripped,
                "document_type": "fundamentals",
            }
            for chunk in split_documents
        ]

        # Ingest using the existing company ingestion service
        chunks_created = company_ingestion_service.ingest_documents(
            company=company_stripped,
            source="yfinance",
            documents=chunk_texts,
            metadata=chunk_metadata,
        )

        return {
            "company": company_stripped,
            "chunks_created": chunks_created,
            "status": "success",
        }

    def _build_document_text(self, fundamentals: dict[str, Any]) -> str:
        """Convert structured fundamentals data to natural-language document.

        Args:
            fundamentals: Dictionary of fundamentals data

        Returns:
            Formatted text document
        """
        sections = ["Company Fundamentals"]

        # Company
        sections.append(f"Company: {fundamentals.get('company', 'N/A')}")

        # Current Price
        current_price = fundamentals.get("current_price")
        if current_price is not None:
            sections.append(f"Current Price: ₹{current_price:.2f}")

        # Market Capitalization
        market_cap = fundamentals.get("market_cap")
        if market_cap is not None:
            # Convert to lakh crore if large enough
            if market_cap >= 1e12:
                market_cap_str = f"₹{market_cap / 1e12:.2f} lakh crore"
            elif market_cap >= 1e7:
                market_cap_str = f"₹{market_cap / 1e7:.2f} crore"
            else:
                market_cap_str = f"₹{market_cap:,.0f}"
            sections.append(f"Market Capitalization: {market_cap_str}")

        # P/E Ratio
        pe_ratio = fundamentals.get("pe_ratio")
        if pe_ratio is not None:
            sections.append(f"P/E Ratio: {pe_ratio:.2f}")

        # P/B Ratio
        pb_ratio = fundamentals.get("pb_ratio")
        if pb_ratio is not None:
            sections.append(f"P/B Ratio: {pb_ratio:.2f}")

        # EPS
        eps = fundamentals.get("eps")
        if eps is not None:
            sections.append(f"EPS: {eps:.2f}")

        # ROE
        roe = fundamentals.get("roe")
        if roe is not None:
            sections.append(f"ROE: {roe:.1f}%")

        # Dividend Yield
        dividend_yield = fundamentals.get("dividend_yield")
        if dividend_yield is not None:
            sections.append(f"Dividend Yield: {dividend_yield:.1f}%")

        # Debt to Equity
        debt_to_equity = fundamentals.get("debt_to_equity")
        if debt_to_equity is not None:
            sections.append(f"Debt to Equity: {debt_to_equity:.2f}")

        # Book Value
        book_value = fundamentals.get("book_value")
        if book_value is not None:
            sections.append(f"Book Value: ₹{book_value:.2f}")

        # 52 Week High
        fifty_two_week_high = fundamentals.get("fifty_two_week_high")
        if fifty_two_week_high is not None:
            sections.append(f"52 Week High: ₹{fifty_two_week_high:.2f}")

        # 52 Week Low
        fifty_two_week_low = fundamentals.get("fifty_two_week_low")
        if fifty_two_week_low is not None:
            sections.append(f"52 Week Low: ₹{fifty_two_week_low:.2f}")

        # Sector
        sector = fundamentals.get("sector")
        if sector:
            sections.append(f"Sector:\n{sector}")

        # Industry
        industry = fundamentals.get("industry")
        if industry:
            sections.append(f"Industry:\n{industry}")

        # Business Summary
        business_summary = fundamentals.get("business_summary")
        if business_summary:
            sections.append(f"Business Summary:\n{business_summary}")

        sections.append(f"Source: yfinance")
        sections.append(f"Resolved Ticker: {fundamentals.get('resolved_ticker', 'N/A')}")

        return "\n\n".join(sections)

    def _build_metadata(self, fundamentals: dict[str, Any]) -> dict[str, Any]:
        """Build metadata for the fundamentals document.

        Args:
            fundamentals: Dictionary of fundamentals data

        Returns:
            Metadata dictionary
        """
        return {
            "company": fundamentals.get("company"),
            "document_type": "fundamentals",
            "source": "yfinance",
            "resolved_ticker": fundamentals.get("resolved_ticker"),
        }


fundamentals_ingestion_service = FundamentalsIngestionService()
