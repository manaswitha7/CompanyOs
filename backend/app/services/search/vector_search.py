from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.chunk import DocumentChunk
from app.models.document import Document

from app.services.embeddings.embedder import embedding_service

from app.services.permissions.document_access import (
    get_accessible_document_ids,
)

from app.services.permissions.roles import Role


# ============================================================
# ACCESSIBLE DOCUMENT IDS
# ============================================================


def _get_accessible_ids(
    db: Session,
    user_id: int,
    role: str | Role,
    workspace_id: int,
) -> list[int]:
    """
    Return document IDs the current user is allowed to read.

    Access is restricted to:

    1. Documents owned by the user
    2. Documents explicitly shared with the user

    The permission layer also verifies that the role has
    DOCUMENTS_READ permission.
    """

    return get_accessible_document_ids(
        db=db,
        user_id=user_id,
        role=role,
        workspace_id=workspace_id,
    )


# ============================================================
# SEMANTIC SEARCH
# ============================================================


def semantic_search(
    db: Session,
    query: str,
    workspace_id: int,
    user_id: int,
    role: str | Role,
    top_k: int = 10,
    document_id: int | None = None,
):
    """
    Semantic retrieval using pgvector cosine similarity.

    Retrieval is restricted to documents that the
    authenticated user is allowed to read.
    """

    if not query or not query.strip():
        return []

    query = query.strip()

    # --------------------------------------------------------
    # Get accessible documents
    # --------------------------------------------------------

    accessible_document_ids = _get_accessible_ids(
        db=db,
        user_id=user_id,
        role=role,
        workspace_id=workspace_id,
    )

    if not accessible_document_ids:
        return []

    # --------------------------------------------------------
    # Optional document filter
    # --------------------------------------------------------

    if document_id is not None:

        if document_id not in accessible_document_ids:
            return []

        accessible_document_ids = [
            document_id
        ]

    # --------------------------------------------------------
    # Create query embedding
    # --------------------------------------------------------

    query_embedding = embedding_service.embed_text(
        query
    )

    similarity = (
        1
        - DocumentChunk.embedding.cosine_distance(
            query_embedding
        )
    ).label("similarity")

    # --------------------------------------------------------
    # Build query
    # --------------------------------------------------------

    query_obj = (
        db.query(
            DocumentChunk,
            Document.filename,
            similarity,
        )
        .join(
            Document,
            Document.id == DocumentChunk.document_id,
        )
        .filter(
            DocumentChunk.embedding.is_not(None)
        )
        .filter(
            Document.workspace_id == workspace_id
        )
        .filter(
            DocumentChunk.document_id.in_(
                accessible_document_ids
            )
        )
    )

    # --------------------------------------------------------
    # Execute
    # --------------------------------------------------------

    return (
        query_obj
        .order_by(similarity.desc())
        .limit(top_k)
        .all()
    )


# ============================================================
# KEYWORD SEARCH
# ============================================================


def keyword_search(
    db: Session,
    query: str,
    workspace_id: int,
    user_id: int,
    role: str | Role,
    top_k: int = 10,
    document_id: int | None = None,
):
    """
    PostgreSQL full-text keyword search.

    Retrieval is restricted to documents that the
    authenticated user is allowed to read.
    """

    if not query or not query.strip():
        return []

    query = query.strip()

    # --------------------------------------------------------
    # Get accessible documents
    # --------------------------------------------------------

    accessible_document_ids = _get_accessible_ids(
        db=db,
        user_id=user_id,
        role=role,
        workspace_id=workspace_id,
    )

    if not accessible_document_ids:
        return []

    # --------------------------------------------------------
    # Optional document filter
    # --------------------------------------------------------

    if document_id is not None:

        if document_id not in accessible_document_ids:
            return []

        accessible_document_ids = [
            document_id
        ]

    # --------------------------------------------------------
    # PostgreSQL full-text search
    # --------------------------------------------------------

    search_vector = func.to_tsvector(
        "english",
        DocumentChunk.content,
    )

    search_query = func.plainto_tsquery(
        "english",
        query,
    )

    keyword_score = func.ts_rank(
        search_vector,
        search_query,
    ).label("keyword_score")

    # --------------------------------------------------------
    # Build query
    # --------------------------------------------------------

    query_obj = (
        db.query(
            DocumentChunk,
            Document.filename,
            keyword_score,
        )
        .join(
            Document,
            Document.id == DocumentChunk.document_id,
        )
        .filter(
            search_vector.op("@@")(search_query)
        )
        .filter(
            Document.workspace_id == workspace_id
        )
        .filter(
            DocumentChunk.document_id.in_(
                accessible_document_ids
            )
        )
    )

    # --------------------------------------------------------
    # Execute
    # --------------------------------------------------------

    return (
        query_obj
        .order_by(keyword_score.desc())
        .limit(top_k)
        .all()
    )


# ============================================================
# HYBRID SEARCH
# ============================================================


def hybrid_search(
    db: Session,
    query: str,
    workspace_id: int,
    user_id: int,
    role: str | Role,
    top_k: int = 5,
    document_id: int | None = None,
):
    """
    True hybrid retrieval.

    Combines:

        1. PostgreSQL full-text search
        2. pgvector semantic search

    Weighting:

        75% semantic
        25% keyword

    Retrieval is restricted to documents that the
    authenticated user is allowed to read.
    """

    if not query or not query.strip():
        return []

    # --------------------------------------------------------
    # 1. Semantic retrieval
    # --------------------------------------------------------

    semantic_results = semantic_search(
        db=db,
        query=query,
        workspace_id=workspace_id,
        user_id=user_id,
        role=role,
        top_k=20,
        document_id=document_id,
    )

    # --------------------------------------------------------
    # 2. Keyword retrieval
    # --------------------------------------------------------

    keyword_results = keyword_search(
        db=db,
        query=query,
        workspace_id=workspace_id,
        user_id=user_id,
        role=role,
        top_k=20,
        document_id=document_id,
    )

    # --------------------------------------------------------
    # 3. Merge results by chunk ID
    # --------------------------------------------------------

    merged = {}

    # --------------------------------------------------------
    # 4. Add semantic results
    # --------------------------------------------------------

    for (
        chunk,
        filename,
        semantic_score,
    ) in semantic_results:

        chunk_id = chunk.id

        merged[chunk_id] = {
            "chunk": chunk,
            "filename": filename,
            "semantic_score": float(
                semantic_score
            ),
            "keyword_score": 0.0,
        }

    # --------------------------------------------------------
    # 5. Add keyword results
    # --------------------------------------------------------

    for (
        chunk,
        filename,
        keyword_score,
    ) in keyword_results:

        chunk_id = chunk.id

        if chunk_id not in merged:

            merged[chunk_id] = {
                "chunk": chunk,
                "filename": filename,
                "semantic_score": 0.0,
                "keyword_score": 0.0,
            }

        merged[chunk_id][
            "keyword_score"
        ] = float(keyword_score)

    # --------------------------------------------------------
    # 6. Normalize keyword scores
    # --------------------------------------------------------

    max_keyword_score = max(
        (
            result["keyword_score"]
            for result in merged.values()
        ),
        default=0.0,
    )

    if max_keyword_score > 0:

        for result in merged.values():

            result["keyword_score"] = (
                result["keyword_score"]
                / max_keyword_score
            )

    # --------------------------------------------------------
    # 7. Calculate hybrid score
    # --------------------------------------------------------

    scored_results = []

    for result in merged.values():

        semantic_score = result[
            "semantic_score"
        ]

        keyword_score = result[
            "keyword_score"
        ]

        final_score = (
            0.75 * semantic_score
            + 0.25 * keyword_score
        )

        result["final_score"] = final_score

        scored_results.append(result)

    # --------------------------------------------------------
    # 8. Sort
    # --------------------------------------------------------

    scored_results.sort(
        key=lambda item: item["final_score"],
        reverse=True,
    )

    # --------------------------------------------------------
    # 9. Return top results
    # --------------------------------------------------------

    return [
        {
            "chunk": result["chunk"],
            "filename": result["filename"],
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
        for result in scored_results[:top_k]
    ]
