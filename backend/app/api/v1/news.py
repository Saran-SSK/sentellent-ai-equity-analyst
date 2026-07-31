from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.ingestion.news_ingestion import news_ingestion_service
from app.schemas.news import NewsIngestionRequest, NewsIngestionResponse

router = APIRouter(prefix="/news", tags=["News"])


@router.post(
    "/ingest",
    response_model=NewsIngestionResponse,
    summary="Ingest company news into the vector store",
    description=(
        "Fetch company news from Finnhub, convert it into text documents, "
        "split them into chunks, create embeddings, and store them in Qdrant."
    ),
)
async def ingest_news(request: NewsIngestionRequest) -> NewsIngestionResponse:
    """Ingest company news articles for a date range."""
    try:
        result = news_ingestion_service.ingest_news(
            company=request.company,
            from_date=request.from_date,
            to_date=request.to_date,
        )
        return NewsIngestionResponse(**result)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
