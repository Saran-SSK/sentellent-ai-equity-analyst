from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.ingestion.pdf_ingestion import pdf_ingestion_service
from app.schemas.ingestion import PDFIngestionResponse

router = APIRouter(
    prefix="/ingestion",
    tags=["Ingestion"],
)


@router.post(
    "/pdf",
    response_model=PDFIngestionResponse,
    summary="Ingest a company annual report PDF",
    description=(
        "Upload a PDF annual report, split it into chunks, generate embeddings, "
        "and store them in Qdrant."
    ),
)
async def ingest_pdf(
    company: str = Form(...),
    source: str | None = Form(None),
    file: UploadFile = File(...),
) -> PDFIngestionResponse:
    """Upload and ingest a company annual report PDF."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded filename is required.",
        )

    if Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    temp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        chunks = pdf_ingestion_service.ingest_pdf(
            pdf_path=temp_path,
            company=company,
            source=source,
        )
        return PDFIngestionResponse(
            message=f"Successfully ingested {chunks} chunks.",
            chunks=chunks,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
