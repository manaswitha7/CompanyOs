from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.services.auth.dependencies import get_current_user
from app.services.permissions.dependencies import require_permission
from app.services.permissions.roles import Permission

from app.services.tools.base import ToolContext
from app.services.tools.registry import tool_registry

import app.services.tools


router = APIRouter(
    prefix="/tools",
    tags=["Tools"],
)


class ToolExecuteRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = {}


@router.get("")
def list_tools():
    return {
        "tools": tool_registry.list_tools()
    }


@router.get("/{tool_name}")
def get_tool(
    tool_name: str,
):
    tool = tool_registry.get(tool_name)

    if not tool:
        raise HTTPException(
            status_code=404,
            detail="Tool not found",
        )

    return tool.schema()


@router.post("/execute")
def execute_tool(
    request: ToolExecuteRequest,
    current_user: User = Depends(
        require_permission(
            Permission.CHAT_USE
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Execute a Company OS tool in the context of
    the authenticated user and workspace.
    """

    tool = tool_registry.get(
        request.tool_name
    )

    if not tool:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Tool '{request.tool_name}' "
                "not found"
            ),
        )

    if current_user.workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to a workspace.",
        )

    context = ToolContext(
        workspace_id=current_user.workspace_id,
        user_id=current_user.id,
        db=db,
    )

    try:

        result = tool_registry.execute(
            name=request.tool_name,
            context=context,
            arguments=request.arguments,
        )

        return {
            "success": True,
            "tool": request.tool_name,
            "result": result,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
