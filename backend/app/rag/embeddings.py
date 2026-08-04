from __future__ import annotations

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Service for generating normalized text embeddings."""

    def __init__(self) -> None:
        self._model = None

    def _get_model(self):
        if self._model is None:
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
        return self._model

    def embed_query(self, text: str) -> list[float]:
        if not text:
            raise ValueError("Text is required to generate an embedding.")

        embedding = self._get_model().encode(
            text,
            normalize_embeddings=True,
        )
        return embedding.tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            raise ValueError("Texts are required to generate embeddings.")
        if any(not text for text in texts):
            raise ValueError("All texts must be non-empty.")

        embeddings = self._get_model().encode(
            texts,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def embedding_dimension(self) -> int:
        return self._get_model().get_sentence_embedding_dimension()


embedding_service = EmbeddingService()