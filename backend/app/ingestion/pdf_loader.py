from __future__ import annotations

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from pypdf.errors import PdfReadError


class PDFLoader:
    """Loader for reading PDF files into LangChain documents."""

    def load(self, pdf_path: str) -> list[Document]:
        """Load all pages from a PDF file as LangChain documents."""
        if not pdf_path or not pdf_path.strip():
            raise ValueError("PDF path is required.")

        path = Path(pdf_path).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            loader = PyPDFLoader(str(path))
            return loader.load()
        except PdfReadError as exc:
            raise ValueError(f"Invalid PDF file: {pdf_path}") from exc
        except Exception as exc:
            raise RuntimeError(f"Failed to load PDF '{pdf_path}'.") from exc


pdf_loader = PDFLoader()
