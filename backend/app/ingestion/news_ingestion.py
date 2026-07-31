from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

import requests
from langchain_core.documents import Document

from app.ingestion.text_splitter import text_splitter
from app.ingestion.company_ingestion import company_ingestion_service
from app.providers.finnhub_provider import finnhub_provider
from app.utils.company_normalizer import to_canonical_company_id


class NewsIngestionService:
    """Service for ingesting company news articles into the document store."""

    def ingest_news(
        self,
        company: str,
        from_date: date,
        to_date: date,
    ) -> dict[str, Any]:
        """Fetch news for a company, split it into chunks, and ingest it into Qdrant."""
        if not company or not company.strip():
            raise ValueError("Company is required for news ingestion.")

        if from_date > to_date:
            raise ValueError("from_date must be on or before to_date.")

        # Convert company to canonical identifier (e.g., "Apple" -> "AAPL")
        company_canonical = to_canonical_company_id(company)

        try:
            raw_news = finnhub_provider.get_company_news(
                symbol=company_canonical,
                from_date=from_date.isoformat(),
                to_date=to_date.isoformat(),
            )
        except requests.RequestException as exc:
            raise RuntimeError(f"Finnhub request failed: {exc}") from exc

        if not raw_news:
            raise ValueError("No news articles were returned for the requested period.")

        documents: list[Document] = []
        chunk_metadata: list[dict[str, Any]] = []

        for article in raw_news:
            document_text = self._build_document_text(article)
            metadata = self._build_metadata(article)
            documents.append(Document(page_content=document_text, metadata=metadata))

        if not documents:
            raise ValueError("No news articles could be converted into documents.")

        split_documents = text_splitter.split(documents)

        chunk_texts = [
            chunk.page_content.strip()
            for chunk in split_documents
            if chunk.page_content and chunk.page_content.strip()
        ]

        chunk_metadata = [
            {
                **(chunk.metadata or {}),
                "company": company_canonical,
                "document_type": "news",
            }
            for chunk in split_documents
        ]

        chunks_created = company_ingestion_service.ingest_documents(
            company=company_canonical,
            source="news",
            documents=chunk_texts,
            metadata=chunk_metadata,
        )

        return {
            "company": company_canonical,
            "articles_ingested": len(raw_news),
            "chunks_created": chunks_created,
            "status": "success",
        }

    def _build_document_text(self, article: dict[str, Any]) -> str:
        """Create a single text document from a Finnhub article."""
        headline = str(article.get("headline") or "Untitled").strip()
        summary = str(article.get("summary") or article.get("headline") or "").strip()
        source = str(article.get("source") or "Unknown").strip()
        published_at = self._normalize_datetime(article.get("datetime"))
        url = str(article.get("url") or "").strip()

        sections = [
            f"Headline:\n{headline}",
            f"Summary:\n{summary}",
            f"Source:\n{source}",
            f"Published:\n{published_at}",
            f"URL:\n{url}",
        ]
        return "\n\n".join(sections)

    def _build_metadata(self, article: dict[str, Any]) -> dict[str, Any]:
        """Build metadata for a single news article document."""
        return {
            "company": None,
            "headline": str(article.get("headline") or "Untitled").strip(),
            "source": str(article.get("source") or "Unknown").strip(),
            "published_at": self._normalize_datetime(article.get("datetime")),
            "url": str(article.get("url") or "").strip(),
            "document_type": "news",
        }

    def _normalize_datetime(self, value: Any) -> str:
        """Normalize Finnhub datetime values into a readable string."""
        if value is None:
            return ""

        if isinstance(value, datetime):
            return value.astimezone(timezone.utc).isoformat()

        if isinstance(value, (int, float)):
            try:
                return datetime.fromtimestamp(int(value), tz=timezone.utc).isoformat()
            except (OverflowError, OSError, ValueError):
                return str(value)

        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return ""
            try:
                return datetime.fromisoformat(
                    stripped.replace("Z", "+00:00")
                ).isoformat()
            except ValueError:
                return stripped

        return str(value)


news_ingestion_service = NewsIngestionService()
