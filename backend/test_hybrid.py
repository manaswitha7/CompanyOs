from app.database.database import SessionLocal
from app.services.search.vector_search import hybrid_search


db = SessionLocal()

try:

    results = hybrid_search(
        db=db,
        query="NeuroBiomeX",
        workspace_id=1,
        user_id=1,
        role="member",
        top_k=5,
    )

    print("\nTRUE HYBRID SEARCH RESULTS")
    print("=" * 70)

    for result in results:

        chunk = result["chunk"]

        print(
            f"Chunk: {chunk.id}"
        )

        print(
            f"Filename: {result['filename']}"
        )

        print(
            f"Page: {chunk.page_number}"
        )

        print(
            f"Semantic: "
            f"{result['semantic_score']:.4f}"
        )

        print(
            f"Keyword: "
            f"{result['keyword_score']:.4f}"
        )

        print(
            f"Final: "
            f"{result['final_score']:.4f}"
        )

        print(
            f"Content: "
            f"{chunk.content[:300]}"
        )

        print("-" * 70)

finally:
    db.close()
