from sqlalchemy.orm import Session

from app.services.context.cross_team import (
    get_cross_team_context,
)
from app.services.rag.retriever import retrieve_chunks


def retrieve_cross_team_context(
    db: Session,
    query: str,
    user_id: int,
    workspace_id: int,
    role: str,
    top_k: int = 5,
) -> dict:
    """
    Retrieve permission-aware information across
    organizational and business context.
    """

    if not query or not query.strip():
        return {
            "query": query,
            "context": {},
            "results": [],
        }

    # ----------------------------------------------
    # 1. Resolve organizational context
    # ----------------------------------------------

    organizational_context = get_cross_team_context(
        db=db,
        user_id=user_id,
        workspace_id=workspace_id,
    )

    # ----------------------------------------------
    # 2. Retrieve accessible knowledge
    # ----------------------------------------------

    results = retrieve_chunks(
        db=db,
        query=query,
        workspace_id=workspace_id,
        user_id=user_id,
        role=role,
        top_k=top_k,
    )

    # ----------------------------------------------
    # 3. Return unified context
    # ----------------------------------------------

    return {
        "query": query,
        "context": {
            "user": organizational_context["user"],
            "team": organizational_context["team"],
            "department": organizational_context["department"],
            "people": organizational_context["people"],
            "companies": organizational_context["companies"],
            "projects": organizational_context["projects"],
        },
        "results": results,
    }
