from datetime import date
from unittest.mock import MagicMock, patch

from langchain_core.documents import Document

from app.ingestion.news_ingestion import news_ingestion_service


def test_ingest_news_builds_documents_and_forwards_metadata() -> None:
    fake_news = [
        {
            "id": 1,
            "headline": "Acme announces expansion",
            "summary": "Acme expands operations.",
            "source": "Reuters",
            "datetime": 1704067200,
            "url": "https://example.com/news/1",
        }
    ]

    with patch(
        "app.ingestion.news_ingestion.finnhub_provider.get_company_news",
        return_value=fake_news,
    ), patch(
        "app.ingestion.news_ingestion.text_splitter.split",
        return_value=[
            Document(
                page_content="split chunk",
                metadata={"headline": "Acme announces expansion"},
            )
        ],
    ) as split_mock, patch(
        "app.ingestion.news_ingestion.company_ingestion_service.ingest_documents",
        return_value=1,
    ) as ingest_mock:
        result = news_ingestion_service.ingest_news(
            company="AAPL",
            from_date=date(2024, 1, 1),
            to_date=date(2024, 1, 2),
        )

    assert result["articles_ingested"] == 1
    assert result["chunks_created"] == 1
    assert result["status"] == "success"
    split_mock.assert_called_once()
    ingest_mock.assert_called_once()
    _, kwargs = ingest_mock.call_args
    assert kwargs["company"] == "AAPL"
    assert kwargs["source"] == "news"
    assert kwargs["documents"] == ["split chunk"]
    assert kwargs["metadata"][0]["headline"] == "Acme announces expansion"
    assert kwargs["metadata"][0]["document_type"] == "news"
