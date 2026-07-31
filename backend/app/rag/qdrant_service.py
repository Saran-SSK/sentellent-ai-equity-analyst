from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PayloadSchemaType, VectorParams

from app.core.config import settings


class QdrantService:
    """Service wrapper for a configured Qdrant client."""

    def __init__(self) -> None:
        """Initialize the Qdrant client once for reuse."""
        if not settings.qdrant_url:
            raise ValueError("QDRANT_URL is required to initialize QdrantService.")
        if not settings.qdrant_api_key:
            raise ValueError("QDRANT_API_KEY is required to initialize QdrantService.")

        self._client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=120.0,          # Increase timeout to 2 minutes
            prefer_grpc=False,      # Keep HTTP unless you have gRPC configured
        )

    def get_client(self) -> QdrantClient:
        """Return the initialized Qdrant client."""
        return self._client

    def collection_exists(self, collection_name: str) -> bool:
        """Return whether a collection exists in Qdrant."""
        return self._client.collection_exists(collection_name=collection_name)

    def health_check(self) -> bool:
        """Return whether the Qdrant server is reachable."""
        try:
            self._client.get_collections()
            return True
        except Exception as exc:
            print(f"Qdrant health check failed: {exc}")
            return False

    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: Distance = Distance.COSINE,
    ) -> None:
        """Create a collection if it does not already exist."""
        if self.collection_exists(collection_name):
            return

        self._client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=distance,
            ),
        )

        self._client.create_payload_index(
            collection_name=collection_name,
            field_name="company",
            field_schema=PayloadSchemaType.KEYWORD,
        )

        self._client.create_payload_index(
            collection_name=collection_name,
            field_name="source",
            field_schema=PayloadSchemaType.KEYWORD,
        )


qdrant_service = QdrantService()