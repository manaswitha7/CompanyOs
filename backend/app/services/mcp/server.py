from typing import Any

from mcp.server import MCPServer

from app.services.tools.registry import tool_registry
from app.services.tools.setup import register_tools


# ============================================================
# REGISTER COMPANY OS TOOLS
# ============================================================

register_tools()


# ============================================================
# MCP SERVER
# ============================================================

mcp = MCPServer("Company OS")


# ============================================================
# LIST TOOLS
# ============================================================

@mcp.tool()
def list_company_tools() -> list[dict[str, Any]]:
    """
    List all tools registered in Company OS.
    """

    return tool_registry.definitions()


# ============================================================
# SYSTEM HEALTH
# ============================================================

@mcp.tool()
def system_health() -> dict[str, Any]:
    """
    Check whether the Company OS backend is running.
    """

    tool = tool_registry.get("system_health")

    return tool.execute(
        arguments={},
        user_id=0,
        workspace_id=0,
    )


# ============================================================
# CREATE TASK
# ============================================================

@mcp.tool()
def create_task(
    title: str,
    description: str = "",
    user_id: int = 0,
    workspace_id: int = 0,
) -> dict[str, Any]:
    """
    Create a task in a Company OS workspace.
    """

    if not title.strip():
        raise ValueError(
            "Task title cannot be empty."
        )

    if user_id <= 0:
        raise ValueError(
            "A valid user_id is required."
        )

    if workspace_id <= 0:
        raise ValueError(
            "A valid workspace_id is required."
        )

    tool = tool_registry.get("create_task")

    return tool.execute(
        arguments={
            "title": title,
            "description": description,
        },
        user_id=user_id,
        workspace_id=workspace_id,
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    mcp.run()
