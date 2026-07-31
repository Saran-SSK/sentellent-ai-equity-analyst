from __future__ import annotations

from app.agents.equity_analyst import equity_analyst_agent
from app.ingestion.company_ingestion import company_ingestion_service
from app.rag.embeddings import embedding_service
from app.rag.qdrant_service import qdrant_service
from app.rag.retrieval import retrieval_service


def main() -> None:
    """Run a standalone integration test for the RAG pipeline."""
    documents = [
        "Apple generates revenue primarily from iPhone sales, services, and wearables.",
        "Apple's Services business includes iCloud, Apple Music, Apple TV+, and the App Store.",
        "Apple continues investing heavily in AI and custom silicon.",
    ]

    try:
        qdrant_client = qdrant_service.get_client()
        if qdrant_service.collection_exists("company_documents"):
            qdrant_client.delete_collection(collection_name="company_documents")
        qdrant_service.create_collection(
            collection_name="company_documents",
            vector_size=embedding_service.embedding_dimension(),
        )

        ingested_count = company_ingestion_service.ingest_documents(
            company="Apple",
            source="Integration Test",
            documents=documents,
        )
        print(f"✓ Documents ingested: {ingested_count}")

        results = retrieval_service.retrieve(
            query="What are Apple's major revenue sources?",
            company="Apple",
        )

        print("\nRetrieved results:")
        if not results:
            print("No retrieved documents found.")
        for result in results:
            print(f"Score: {result['score']}")
            print(f"Company: {result['company']}")
            print(f"Source: {result['source']}")
            print(f"Chunk: {result['chunk']}")
            print()

        response = equity_analyst_agent.ask(
            question="What are Apple's major revenue sources?",
            company="Apple",
        )

        print("Final AI response:")
        print(response)
    except Exception as exc:
        print(f"RAG pipeline integration test failed: {exc}")


if __name__ == "__main__":
    main()
