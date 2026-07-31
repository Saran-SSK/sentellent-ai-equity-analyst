from __future__ import annotations

from typing import Any

from qdrant_client.models import FieldCondition, Filter, MatchValue

from app.rag.embeddings import embedding_service
from app.rag.qdrant_service import qdrant_service


class RetrievalService:
    """Service for semantic retrieval from Qdrant."""

    def __init__(self, collection_name: str = "company_documents") -> None:
        self._collection_name = collection_name

    def retrieve(
        self,
        query: str,
        company: str | None = None,
        limit: int = 10,  # Increased from 5 to allow mixed document type retrieval
        score_threshold: float = 0.35,  # <-- lowered from 0.6
    ) -> list[dict[str, Any]]:
        """Retrieve semantically relevant document chunks."""

        if not query:
            raise ValueError("Query is required for retrieval.")

        if limit <= 0:
            raise ValueError("Limit must be greater than zero.")

        if score_threshold < 0:
            raise ValueError("Score threshold must be non-negative.")

        query_vector = embedding_service.embed_query(query)

        query_filter = self._build_company_filter(company)

        response = qdrant_service.get_client().query_points(
            collection_name=self._collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
            score_threshold=score_threshold,
            with_payload=True,
        )

        matches = sorted(
            response.points,
            key=lambda x: x.score,
            reverse=True,
        )

        # ---------------- DEBUG ----------------
        print("\n" + "=" * 70)
        print("RETRIEVAL DEBUG")
        print(f"Query           : {query}")
        print(f"Company         : {company}")
        print(f"Threshold       : {score_threshold}")
        print(f"Retrieved       : {len(matches)}")
        print("-" * 70)

        for i, match in enumerate(matches):
            payload = match.payload or {}
            print(
                f"{i+1}. "
                f"Score={match.score:.4f} | "
                f"Type={payload.get('document_type')} | "
                f"Source={payload.get('source')}"
            )

        print("=" * 70 + "\n")
        # ---------------------------------------

        return [
            {
                "score": float(match.score),
                "company": str(payload.get("company", "")),
                "source": str(payload.get("source", "")),
                "chunk": str(payload.get("chunk", "")),
                "timestamp": str(payload.get("timestamp", "")),
                "document_type": str(payload.get("document_type", "")),
                "headline": str(payload.get("headline", "")),
                "published_at": str(payload.get("published_at", "")),
            }
            for match in matches
            for payload in [match.payload or {}]
        ]

    def _build_company_filter(self, company: str | None) -> Filter | None:
        """Build a payload filter for company."""

        if not company:
            return None

        return Filter(
            must=[
                FieldCondition(
                    key="company",
                    match=MatchValue(value=company),
                )
            ]
        )


retrieval_service = RetrievalService()
