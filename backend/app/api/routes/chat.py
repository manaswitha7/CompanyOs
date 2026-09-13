from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.services.auth.dependencies import get_current_user
from app.services.audit.service import create_audit_log
from app.services.rag.generator import generate_rag_answer
from app.services.permissions.dependencies import (
    require_permission,
)
from app.services.agent.company_agent import CompanyAgent
from app.services.tools.base import ToolContext
from app.services.permissions.roles import Permission

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question to ask the Company OS",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of chunks to retrieve",
    )

    document_id: int | None = Field(
        default=None,
        description="Optional document filter",
    )


@router.post("")
def chat(
    request: ChatRequest,
    current_user: User = Depends(
        require_permission(
            Permission.CHAT_USE
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Ask the Company OS a question.

    The question is processed only against
    documents belonging to the authenticated
    user's workspace.
    """

    if current_user.workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to a workspace.",
        )

    try:

        # --------------------------------------------------
        # 1. Generate RAG answer
        # --------------------------------------------------

        result = generate_rag_answer(
            db=db,
            question=request.question,
            user_id=current_user.id,
            role=current_user.role,
            workspace_id=current_user.workspace_id,
            top_k=request.top_k,
            document_id=request.document_id,
        )

        # --------------------------------------------------
        # 2. Create audit record
        # --------------------------------------------------

        create_audit_log(
            db,
            workspace_id=current_user.workspace_id,
            user_id=current_user.id,
            action="CHAT_REQUESTED",
            resource_type="chat",
            details={
                "question_length": len(
                    request.question
                ),
                "top_k": request.top_k,
                "document_id": request.document_id,
            },
        )

        # --------------------------------------------------
        # 3. Commit audit record
        # --------------------------------------------------

        db.commit()

        # --------------------------------------------------
        # 4. Return response
        # --------------------------------------------------

        return {
            "question": request.question,
            "answer": result["answer"],
            "citations": result["citations"],
            "metrics": result.get("metrics"),
        }

    except ValueError as exc:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except HTTPException:

        db.rollback()
        raise

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"RAG generation failed: {str(exc)}",
        )
# ============================================================
# AGENT CHAT
# ============================================================


@router.post("/agent")
def agent_chat(
    request: ChatRequest,
    current_user: User = Depends(
        require_permission(
            Permission.CHAT_USE
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Unified Company OS agent endpoint.

    The agent can:
    - answer using company knowledge through RAG
    - call registered tools when required
    - combine retrieved knowledge and tool results
    """

    if current_user.workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "User is not assigned "
                "to a workspace."
            ),
        )

    try:

        # --------------------------------------------------
        # 1. Create tool/runtime context
        # --------------------------------------------------

        context = ToolContext(
            workspace_id=current_user.workspace_id,
            user_id=current_user.id,
            db=db,
        )

        # --------------------------------------------------
        # 2. Create agent
        # --------------------------------------------------

        agent = CompanyAgent()

        # --------------------------------------------------
        # 3. Run unified agent
        # --------------------------------------------------

        result = agent.run(
            user_message=request.question,
            context=context,
            db=db,
            user_id=current_user.id,
            role=current_user.role,
            workspace_id=current_user.workspace_id,
            top_k=request.top_k,
            document_id=request.document_id,
        )

        # --------------------------------------------------
        # 4. Audit
        # --------------------------------------------------

        create_audit_log(
            db,
            workspace_id=current_user.workspace_id,
            user_id=current_user.id,
            action="AGENT_CHAT_REQUESTED",
            resource_type="agent",
            details={
                "question_length": len(
                    request.question
                ),
                "top_k": request.top_k,
                "document_id": request.document_id,
                "tools_used": [
                    item["tool"]
                    for item in result.get(
                        "tool_calls",
                        [],
                    )
                ],
                "rag_used": result.get(
                    "rag_used",
                    False,
                ),
            },
        )

        # --------------------------------------------------
        # 5. Commit audit
        # --------------------------------------------------

        db.commit()

        # --------------------------------------------------
        # 6. Return response
        # --------------------------------------------------

        return {
            "question": request.question,

            "answer": result.get(
                "answer",
                "",
            ),

            "rag_used": result.get(
                "rag_used",
                False,
            ),

            "used_tools": result.get(
                "used_tools",
                [],
            ),

            "tool_calls": result.get(
                "tool_calls",
                [],
            ),

            "citations": result.get(
                "citations",
                [],
            ),

            "sources": result.get(
                "sources",
                [],
            ),

            "metrics": result.get(
                "metrics",
            ),
        }

    except ValueError as exc:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except HTTPException:

        db.rollback()
        raise

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Agent execution failed: "
                f"{str(exc)}"
            ),
        )
