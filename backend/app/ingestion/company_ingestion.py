from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
import traceback

from qdrant_client.models import PointStruct

from app.rag.embeddings import embedding_service
from app.rag.qdrant_service import qdrant_service


class CompanyIngestionService:
    """Service for ingesting prepared company text chunks into Qdrant."""

    def __init__(self, collection_name: str = "company_documents") -> None:
        self._collection_name = collection_name

    def ingest_documents(
        self,
        company: str,
        source: str,
        documents: list[str],
        metadata: list[dict[str, object]] | None = None,
    ) -> int:
        """Ingest prepared text chunks for a company into Qdrant."""

        if not company:
            raise ValueError("Company is required for document ingestion.")

        if not source:
            raise ValueError("Source is required for document ingestion.")

        if not documents:
            raise ValueError("Documents are required for document ingestion.")

        valid_documents = [
            document.strip() for document in documents if document and document.strip()
        ]

        if not valid_documents:
            return 0

        print(f"Generating embeddings for {len(valid_documents)} chunks...")

        qdrant_service.create_collection(
            collection_name=self._collection_name,
            vector_size=embedding_service.embedding_dimension(),
        )

        embeddings = embedding_service.embed_documents(valid_documents)

        timestamp = datetime.now(timezone.utc).isoformat()

        points = [
            PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "company": company,
                    "source": source,
                    "chunk": document,
                    "timestamp": timestamp,
                    **(
                        metadata[index]
                        if metadata is not None and index < len(metadata)
                        else {}
                    ),
                },
            )
            for index, (document, embedding) in enumerate(
                zip(
                    valid_documents,
                    embeddings,
                    strict=True,
                )
            )
        ]

        try:
            print(f"Ingesting {len(points)} vectors into Qdrant...")

            qdrant_service.get_client().upsert(
                collection_name=self._collection_name,
                points=points,
                wait=True,
            )

            print("Qdrant upsert completed successfully.")

        except Exception as exc:
            print("\n========== QDRANT UPSERT ERROR ==========")
            print(f"Exception Type : {type(exc).__name__}")
            print(f"Exception      : {exc}")
            traceback.print_exc()
            print("=========================================\n")
            raise

        return len(points)


company_ingestion_service = CompanyIngestionService()
