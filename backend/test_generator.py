from app.database.database import SessionLocal
from app.services.rag.generator import generate_rag_answer


db = SessionLocal()

try:

    result = generate_rag_answer(
        db=db,
        question="What is the overall risk?",
        workspace_id=1,
        user_id=1,
        role="member",
        top_k=5,
    )

    print("\nRAG ANSWER")
    print("=" * 70)

    print(result["answer"])

    print("\nCITATIONS")
    print("=" * 70)

    for citation in result["citations"]:

        print(
            f"Document: "
            f"{citation['filename']}"
        )

        print(
            f"Page: "
            f"{citation['page_number']}"
        )

        print(
            f"Chunk: "
            f"{citation['chunk_id']}"
        )

        print("-" * 70)

finally:
    db.close()
