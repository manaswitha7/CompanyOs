from sqlalchemy.orm import Session

from app.services.search.vector_search import hybrid_search
from app.services.permissions.document_access import (
    get_accessible_document_ids,
)


def retrieve_chunks(
    db: Session,
    query: str,
    workspace_id: int,
    user_id: int,
    role: str,
    top_k: int = 5,
    document_id: int | None = None,
):
    """
    Retrieve citation-ready chunks.

    Retrieval is restricted by:

    1. User workspace
    2. User role permissions
    3. Document ownership
    4. Explicit document permissions
    """

    if not query or not query.strip():
        return []

    # --------------------------------------------------
    # 1. Get documents this user can access
    # --------------------------------------------------

    accessible_document_ids = get_accessible_document_ids(
        db=db,
        user_id=user_id,
        role=role,
        workspace_id=workspace_id,
    )

    # User has no accessible documents
    if not accessible_document_ids:
        return []

    # --------------------------------------------------
    # 2. Optional document filter
    # --------------------------------------------------

    if document_id is not None:

        # Requested document is not accessible
        if document_id not in accessible_document_ids:
            return []

        allowed_document_ids = [document_id]

    else:
        allowed_document_ids = accessible_document_ids

    # --------------------------------------------------
    # 3. Hybrid retrieval
    # --------------------------------------------------

    results = hybrid_search(
        db=db,
        query=query,
        workspace_id=workspace_id,
        user_id=user_id,
        role=role,
        top_k=top_k,
        document_id=document_id,
    )

    # --------------------------------------------------
    # 4. Convert to citation-ready format
    # --------------------------------------------------

    retrieved_chunks = []

    for result in results:

        chunk = result["chunk"]

        retrieved_chunks.append(
            {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "filename": result["filename"],
                "chunk_index": chunk.chunk_index,
                "page_number": chunk.page_number,
                "content": chunk.content,
                "semantic_score": result[
                    "semantic_score"
                ],
                "keyword_score": result[
                    "keyword_score"
                ],
                "final_score": result[
                    "final_score"
                ],
            }
        )

    return retrieved_chunks
