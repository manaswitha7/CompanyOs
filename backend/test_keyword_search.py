from app.database.database import SessionLocal
from app.services.search.vector_search import keyword_search


db = SessionLocal()

try:

    results = keyword_search(
        db=db,
        query="NeuroBiomeX",
        workspace_id=1,
        user_id=1,
        role="member",
        top_k=5,
    )

    print("\nKEYWORD SEARCH RESULTS")
    print("=" * 70)

    for chunk, filename, score in results:

        print(f"Chunk: {chunk.id}")
        print(f"Filename: {filename}")
        print(f"Page: {chunk.page_number}")
        print(f"Keyword score: {score}")
        print(f"Content: {chunk.content[:300]}")

        print("-" * 70)

finally:
    db.close()
