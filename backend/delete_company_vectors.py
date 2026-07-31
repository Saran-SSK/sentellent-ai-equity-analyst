"""
Utility to delete vectors for a specific company identifier.

This script is used to clean up vectors with incorrect company identifiers
before re-ingesting with the correct canonical identifier.

Usage:
    python delete_company_vectors.py <company_name>
    
Example:
    python delete_company_vectors.py Apple
"""

from __future__ import annotations

import sys

from collections import Counter
from qdrant_client.models import FieldCondition, Filter, FilterSelector, MatchValue

from app.rag.qdrant_service import qdrant_service


def delete_company_vectors(
    collection_name: str = "company_documents",
    company: str = "Apple",
) -> int:
    """Delete all vectors for a specific company identifier."""
    
    # Use the project's existing Qdrant service
    client = qdrant_service.get_client()
    
    if not client.collection_exists(collection_name):
        print(f"Collection '{collection_name}' does not exist.")
        return 0
    
    print(f"\nPreparing to delete vectors for company: {company}")
    print(f"Collection: {collection_name}")
    print("=" * 70)
    
    # First, count how many vectors will be deleted
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
            point_company = payload.get("company", "")
            if point_company:
                company_counts[point_company] += 1
            total_points += 1
        
        if offset is None:
            break
    
    print(f"\nCurrent company distribution:")
    for comp, count in sorted(company_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {comp}: {count} points")
    
    if company not in company_counts:
        print(f"\nNo vectors found for company: {company}")
        print("Nothing to delete.")
        return 0
    
    points_to_delete = company_counts[company]
    print(f"\nVectors to delete: {points_to_delete}")
    
    # Confirm deletion
    print("\n" + "!" * 70)
    print("WARNING: This will permanently delete vectors from the database!")
    print(f"Company: {company}")
    print(f"Count: {points_to_delete}")
    print("!" * 70)
    
    confirmation = input("\nProceed with deletion? (yes/no): ").strip().lower()
    
    if confirmation != "yes":
        print("Deletion cancelled by user.")
        return 0
    
    # Delete using filter
    print(f"\nDeleting vectors for company: {company}...")
    
    try:
        client.delete(
            collection_name=collection_name,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="company",
                            match=MatchValue(value=company),
                        )
                    ]
                )
            ),
        )
        
        print(f"Successfully deleted {points_to_delete} vectors for company: {company}")
        
        # Verify deletion
        print("\nVerifying deletion...")
        company_counts_after = Counter()
        offset = None
        
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
                point_company = payload.get("company", "")
                if point_company:
                    company_counts_after[point_company] += 1
            
            if offset is None:
                break
        
        print(f"\nCompany distribution after deletion:")
        for comp, count in sorted(company_counts_after.items(), key=lambda x: x[1], reverse=True):
            print(f"  {comp}: {count} points")
        
        if company not in company_counts_after:
            print(f"\n✓ Verification successful: No vectors remain for company: {company}")
        else:
            print(f"\n✗ Verification failed: {company_counts_after[company]} vectors still exist")
        
        print("=" * 70)
        
        return points_to_delete
        
    except Exception as e:
        print(f"\nError during deletion: {e}")
        return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python delete_company_vectors.py <company_name>")
        print("Example: python delete_company_vectors.py Apple")
        sys.exit(1)
    
    company_to_delete = sys.argv[1]
    delete_company_vectors(company=company_to_delete)
