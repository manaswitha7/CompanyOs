from app.database.database import SessionLocal
from app.services.rag.retriever import retrieve_chunks


db = SessionLocal()

try:
    results = retrieve_chunks(
        db=db,
        query="NeuroBiomeX",
        workspace_id=1,
        user_id=1,
        role="owner",
        top_k=5,
    )

    print("\nRetrieved chunks:")
    print("-" * 60)

    for result in results:
        print(
            f"Chunk: {result['chunk_id']}"
        )
        print(
            f"Page: {result['page_number']}"
        )
        print(
            f"Score: {result['final_score']:.4f}"
        )
        print(
            f"Content: {result['content'][:200]}"
        )
        print("-" * 60)

finally:
    db.close()
