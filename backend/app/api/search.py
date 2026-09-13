from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.services.auth.dependencies import get_current_user
from app.services.permissions.dependencies import require_permission
from app.services.permissions.roles import Permission
from app.services.search.vector_search import (
    semantic_search,
    hybrid_search,
)


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


# ============================================================
# SEMANTIC SEARCH
# ============================================================

@router.get("/semantic")
def semantic_search_endpoint(
    q: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=20),
    document_id: int | None = Query(None),
    current_user: User = Depends(
        require_permission(
            Permission.DOCUMENTS_READ
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Perform permission-aware semantic search.

    Search is restricted to the authenticated
    user's workspace.
    """

    if current_user.workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to a workspace.",
        )

    results = semantic_search(
        db=db,
        query=q,
        workspace_id=current_user.workspace_id,
        user_id=current_user.id,
        role=current_user.role,
        top_k=top_k,
        document_id=document_id,
    )

    response_results = []

    for (
        chunk,
        filename,
        score,
    ) in results:

        response_results.append(
            {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "filename": filename,
                "chunk_index": chunk.chunk_index,
                "page_number": chunk.page_number,
                "similarity": float(score),
                "content": chunk.content,
            }
        )

    return {
        "query": q,
        "results": response_results,
    }


# ============================================================
# HYBRID SEARCH
# ============================================================

@router.get("/hybrid")
def hybrid_search_endpoint(
    q: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=20),
    document_id: int | None = Query(None),
    current_user: User = Depends(
        require_permission(
            Permission.DOCUMENTS_READ
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Perform permission-aware hybrid search.

    Combines:

        semantic search
        +
        keyword search

    Search is restricted to the authenticated
    user's workspace.
    """

    if current_user.workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to a workspace.",
        )

    results = hybrid_search(
        db=db,
        query=q,
        workspace_id=current_user.workspace_id,
        user_id=current_user.id,
        role=current_user.role,
        top_k=top_k,
        document_id=document_id,
    )

    return {
        "query": q,
        "results": [
            {
                "chunk_id": result["chunk"].id,
                "document_id": result["chunk"].document_id,
                "filename": result["filename"],
                "chunk_index": result["chunk"].chunk_index,
                "page_number": result["chunk"].page_number,
                "semantic_score": result[
                    "semantic_score"
                ],
                "keyword_score": result[
                    "keyword_score"
                ],
                "final_score": result[
                    "final_score"
                ],
                "content": result["chunk"].content,
            }
            for result in results
        ],
    }
