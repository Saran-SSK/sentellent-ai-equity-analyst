"""
Migration script to add document_type metadata to existing vectors.

This script updates vectors that were ingested before document_type was added.
It infers document_type based on payload metadata:
- If published_at exists -> document_type = "news"
- Elif headline exists -> document_type = "news"
- Else -> document_type = "annual_report"

Usage:
    python migrate_document_type.py
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from qdrant_client.models import PayloadSchemaType

from app.rag.qdrant_service import qdrant_service


def sample_payloads(
    collection_name: str = "company_documents", sample_size: int = 10
) -> tuple[list[dict], set[str]]:
    """Sample payloads to analyze existing data structure."""

    client = qdrant_service.get_client()

    # Check if collection exists
    if not client.collection_exists(collection_name):
        print(f"Collection '{collection_name}' does not exist.")
        return [], set()

    print(f"\nSampling {sample_size} payloads from collection: {collection_name}")
    print("=" * 70)

    samples = []
    unique_companies = set()
    offset = None
    batch_size = 100

    while len(samples) < sample_size:
        # Retrieve a batch of points
        points, offset = client.scroll(
            collection_name=collection_name,
            limit=batch_size,
            offset=offset,
            with_payload=True,
        )

        if not points:
            break

        for point in points:
            if len(samples) >= sample_size:
                break

            payload = point.payload or {}
            samples.append(payload)

            # Track unique companies
            company = payload.get("company", "")
            if company:
                unique_companies.add(company)

        # Stop if we've processed all points
        if offset is None:
            break

    # Print samples
    for i, payload in enumerate(samples, 1):
        print(f"\n--- Sample {i} ---")
        print(f"Company: {payload.get('company', 'N/A')}")
        print(f"Source: {payload.get('source', 'N/A')}")
        print(f"Headline: {payload.get('headline', 'N/A')}")
        print(f"Published At: {payload.get('published_at', 'N/A')}")
        print(f"Document Type (existing): {payload.get('document_type', 'N/A')}")
        print(f"Payload Keys: {list(payload.keys())}")

        # Determine inferred document_type
        published_at = payload.get("published_at")
        headline = payload.get("headline")

        if published_at:
            inferred = "news"
        elif headline:
            inferred = "news"
        else:
            inferred = "annual_report"

        print(f"Inferred Document Type: {inferred}")

    print("\n" + "=" * 70)
    print(f"Unique companies found: {sorted(unique_companies)}")
    print(f"Total unique companies: {len(unique_companies)}")
    print("=" * 70)

    return samples, unique_companies


def migrate_document_types(collection_name: str = "company_documents") -> None:
    """Add document_type metadata to existing vectors in the collection."""

    client = qdrant_service.get_client()

    # Check if collection exists
    if not client.collection_exists(collection_name):
        print(f"Collection '{collection_name}' does not exist.")
        return

    # Sample payloads to verify the approach
    samples, unique_companies = sample_payloads(collection_name, sample_size=10)

    if not samples:
        print("No samples found. Collection may be empty.")
        return

    # Ask for confirmation
    print("\n" + "=" * 70)
    print("Please review the sample output above.")
    print("If the inferred document types look correct, type 'yes' to proceed.")
    print("Otherwise, type 'no' to cancel.")
    print("=" * 70)

    confirmation = input("\nProceed with migration? (yes/no): ").strip().lower()

    if confirmation != "yes":
        print("Migration cancelled by user.")
        return

    print(f"\nStarting migration for collection: {collection_name}")

    # Scroll through all points in the collection
    offset = None
    total_updated = 0
    total_skipped = 0
    batch_size = 100

    while True:
        # Retrieve a batch of points
        points, offset = client.scroll(
            collection_name=collection_name,
            limit=batch_size,
            offset=offset,
            with_payload=True,
        )

        if not points:
            break

        points_to_update = []
        document_types_to_set = []

        for point in points:
            payload = point.payload or {}
            point_id = point.id

            # Skip if document_type already exists
            if payload.get("document_type"):
                total_skipped += 1
                continue

            # Infer document_type from payload metadata
            published_at = payload.get("published_at")
            headline = payload.get("headline")

            if published_at:
                document_type = "news"
            elif headline:
                document_type = "news"
            else:
                # Assume annual_report for PDFs and other sources
                document_type = "annual_report"

            points_to_update.append(point_id)
            document_types_to_set.append(document_type)
            total_updated += 1

        # Apply updates in batch
        if points_to_update:
            # Update each point with its specific document_type
            for point_id, doc_type in zip(points_to_update, document_types_to_set):
                client.set_payload(
                    collection_name=collection_name,
                    payload={"document_type": doc_type},
                    points=[point_id],
                )

        print(
            f"Processed batch: {len(points)} points, Updated: {total_updated}, Skipped: {total_skipped}"
        )

        # Stop if we've processed all points
        if offset is None:
            break

    print(f"\nMigration complete!")
    print(f"Total points updated: {total_updated}")
    print(f"Total points skipped (already had document_type): {total_skipped}")

    # Create payload index for document_type if it doesn't exist
    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name="document_type",
            field_schema=PayloadSchemaType.KEYWORD,
        )
        print("Created payload index for document_type field.")
    except Exception as e:
        print(f"Payload index may already exist: {e}")


def verify_migration(collection_name: str = "company_documents") -> None:
    """Verify the migration results and test mixed retrieval using the actual retrieval pipeline."""
    
    client = qdrant_service.get_client()
    
    if not client.collection_exists(collection_name):
        print(f"Collection '{collection_name}' does not exist.")
        return
    
    print("\n" + "=" * 70)
    print("MIGRATION VERIFICATION")
    print("=" * 70)
    
    # Count document types
    doc_type_counts = Counter()
    company_counts = Counter()
    offset = None
    batch_size = 100
    total_points = 0
    
    while True:
        points, offset = client.scroll(
            collection_name=collection_name,
            limit=batch_size,
            offset=offset,
            with_payload=True,
        )
        
        if not points:
            break
        
        for point in points:
            payload = point.payload or {}
            doc_type = payload.get("document_type", "None")
            company = payload.get("company", "None")
            
            doc_type_counts[doc_type] += 1
            company_counts[company] += 1
            total_points += 1
        
        if offset is None:
            break
    
    print(f"\nTotal points: {total_points}")
    print(f"\nDocument type distribution:")
    for doc_type, count in sorted(doc_type_counts.items()):
        print(f"  {doc_type}: {count}")
    
    print(f"\nCompany distribution:")
    for company, count in sorted(company_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {company}: {count}")
    
    # Test mixed retrieval using the actual retrieval service
    print("\n" + "=" * 70)
    print("TESTING MIXED RETRIEVAL USING ACTUAL PIPELINE")
    print("=" * 70)
    
    from app.rag.retrieval import retrieval_service
    
    test_query = "How do the latest news affect Apple's long-term financial outlook?"
    test_company = "AAPL"
    
    print(f"\nTest query: {test_query}")
    print(f"Test company: {test_company}")
    
    retrieved_chunks = retrieval_service.retrieve(
        query=test_query,
        company=test_company,
        limit=10,
        score_threshold=0.35,
    )
    
    print(f"\nRetrieved {len(retrieved_chunks)} chunks:")
    print("-" * 70)
    
    annual_report_count = 0
    news_count = 0
    
    for i, chunk in enumerate(retrieved_chunks, 1):
        doc_type = chunk.get("document_type", "None")
        company = chunk.get("company", "None")
        source = chunk.get("source", "None")
        score = chunk.get("score", 0.0)
        
        if doc_type == "annual_report":
            annual_report_count += 1
        elif doc_type == "news":
            news_count += 1
        
        print(f"{i}. Score={score:.4f} | Type={doc_type} | Company={company} | Source={source}")
    
    print("-" * 70)
    print(f"\nRetrieval summary:")
    print(f"  Annual reports: {annual_report_count}")
    print(f"  News articles: {news_count}")
    
    if annual_report_count > 0 and news_count > 0:
        print("\n✓ SUCCESS: Mixed retrieval working correctly!")
    else:
        print("\n✗ FAILURE: Mixed retrieval not working correctly.")
        print("  Expected both annual_report and news document types.")
    
    print("=" * 70)


if __name__ == "__main__":
    import sys
    
    collection_name = "company_documents"
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--verify":
            verify_migration(collection_name)
        else:
            print("Usage:")
            print("  python migrate_document_type.py              # Run full migration")
            print("  python migrate_document_type.py --verify     # Verify migration")
    else:
        migrate_document_types(collection_name)
