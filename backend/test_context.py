from app.database.database import SessionLocal
from app.services.rag.retriever import retrieve_chunks
from app.services.rag.context import build_context


db = SessionLocal()

try:

    results = retrieve_chunks(
        db=db,
        query="NeuroBiomeX",
        workspace_id=1,
        user_id=1,
        role="member",
        top_k=5,
    )

    context = build_context(
        results
    )

    print("\nGenerated RAG Context")
    print("=" * 70)
    print(context)

finally:
    db.close()
