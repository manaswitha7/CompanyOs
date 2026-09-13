from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.services.auth.dependencies import get_current_user
from app.services.agent.company_agent import CompanyAgent
from app.services.tools.base import ToolContext


router = APIRouter(
    prefix="/agent",
    tags=["Agent"],
)


class AgentRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=1,
        description="Request for the Company OS agent",
    )


@router.post("")
def ask_agent(
    request: AgentRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
) -> dict[str, Any]:

    if current_user.workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to a workspace.",
        )

    try:

        context = ToolContext(
            workspace_id=current_user.workspace_id,
            user_id=current_user.id,
            db=db,
            metadata={},
        )

        agent = CompanyAgent()

        result = agent.ask(
            question=request.question,
            context=context,
        )

        return {
            "success": True,
            "question": request.question,
            "answer": result.get("answer"),
            "tool_called": result.get(
                "tool_called"
            ),
            "tool_arguments": result.get(
                "tool_arguments"
            ),
            "tool_result": result.get(
                "tool_result"
            ),
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {str(exc)}",
        )
