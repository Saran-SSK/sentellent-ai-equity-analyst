from __future__ import annotations

from pathlib import Path

from app.ingestion.company_ingestion import company_ingestion_service
from app.ingestion.pdf_loader import pdf_loader
from app.ingestion.text_splitter import text_splitter
from app.utils.company_normalizer import to_canonical_company_id


class PDFIngestionService:
    """Service for ingesting PDF documents into the company document store."""

    def ingest_pdf(
        self,
        pdf_path: str,
        company: str,
        source: str | None = None,
    ) -> int:
        """Load, split, and ingest a PDF for a company."""
        if not company or not company.strip():
            raise ValueError("Company is required for PDF ingestion.")
        if not pdf_path or not pdf_path.strip():
            raise ValueError("PDF path is required for PDF ingestion.")

        documents = pdf_loader.load(pdf_path)
        chunks = text_splitter.split(documents)
        chunk_texts = [
            chunk.page_content.strip()
            for chunk in chunks
            if chunk.page_content and chunk.page_content.strip()
        ]
        document_source = source if source is not None else Path(pdf_path).name

        if not document_source or not document_source.strip():
            raise ValueError("Source is required for PDF ingestion.")

        # Convert company to canonical identifier (e.g., "Apple" -> "AAPL")
        company_canonical = to_canonical_company_id(company)

        chunk_metadata = [
            {
                "company": company_canonical,
                "document_type": "annual_report",
            }
            for _ in chunk_texts
        ]

        return company_ingestion_service.ingest_documents(
            company=company_canonical,
            source=document_source,
            documents=chunk_texts,
            metadata=chunk_metadata,
        )


pdf_ingestion_service = PDFIngestionService()
