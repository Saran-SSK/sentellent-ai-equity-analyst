from __future__ import annotations

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Service for generating normalized text embeddings."""

    def __init__(self) -> None:
        """Load the embedding model once for reuse."""
        self._model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_query(self, text: str) -> list[float]:
        """Generate a normalized embedding for a single query."""
        if not text:
            raise ValueError("Text is required to generate an embedding.")

        embedding = self._model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate normalized embeddings for multiple documents."""
        if not texts:
            raise ValueError("Texts are required to generate embeddings.")
        if any(not text for text in texts):
            raise ValueError("All texts must be non-empty.")

        embeddings = self._model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def embedding_dimension(self) -> int:
        """Return the embedding dimension for the loaded model."""
        return self._model.get_sentence_embedding_dimension()


embedding_service = EmbeddingService()
