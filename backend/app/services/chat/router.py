from typing import Any

from app.services.tools.base import ToolContext
from app.services.tools.registry import tool_registry


# ============================================================
# TOOL KEYWORDS
# ============================================================

TOOL_KEYWORDS: dict[str, list[str]] = {
    "create_task": [
        "create task",
        "add task",
        "make task",
        "new task",
        "assign task",
    ],
    "system_health": [
        "system health",
        "backend health",
        "check health",
        "is the system healthy",
        "is the backend running",
        "check system",
    ],
}


# ============================================================
# DETECT TOOL
# ============================================================

def detect_tool(
    question: str,
) -> str | None:
    """
    Detect the appropriate registered tool for a chat request.

    Returns:
        Registered tool name, or None if the request
        should continue through the normal chat/RAG flow.
    """

    if not question or not question.strip():
        return None

    normalized = question.strip().lower()

    for tool_name, keywords in TOOL_KEYWORDS.items():

        for keyword in keywords:

            if keyword in normalized:

                # Do not attempt execution if the tool
                # isn't actually registered.
                if not tool_registry.exists(tool_name):
                    return None

                return tool_name

    return None


# ============================================================
# EXECUTE TOOL
# ============================================================

def execute_chat_tool(
    tool_name: str,
    arguments: dict[str, Any],
    user_id: int,
    workspace_id: int,
    metadata: dict[str, Any] | None = None,
) -> Any:
    """
    Execute a registered Company OS tool from chat.

    Security rule:
        user_id and workspace_id come from the authenticated
        backend context. They are never taken from the
        user's tool arguments.
    """

    if not tool_registry.exists(tool_name):
        raise ValueError(
            f"Tool '{tool_name}' is not registered."
        )

    context = ToolContext(
        user_id=user_id,
        workspace_id=workspace_id,
        metadata=metadata or {},
    )

    return tool_registry.execute(
        name=tool_name,
        context=context,
        arguments=arguments,
    )


# ============================================================
# BUILD TOOL ARGUMENTS
# ============================================================

def build_tool_arguments(
    tool_name: str,
    question: str,
) -> dict[str, Any]:
    """
    Convert a natural-language chat request into the
    arguments expected by a tool.

    This is intentionally lightweight for the MVP.

    A future Agent Orchestrator can replace this with
    LLM-based structured tool selection.
    """

    normalized = question.strip()

    if tool_name == "system_health":
        return {}

    if tool_name == "create_task":

        # Basic extraction for MVP.
        task_title = normalized

        prefixes = [
            "create task",
            "add task",
            "make task",
            "new task",
            "assign task",
        ]

        lowered = normalized.lower()

        for prefix in prefixes:

            if lowered.startswith(prefix):

                task_title = normalized[
                    len(prefix):
                ].strip()

                break

        if not task_title:
            task_title = "New task"

        return {
            "title": task_title,
        }

    return {}


# ============================================================
# HANDLE CHAT TOOL
# ============================================================

def handle_tool_request(
    question: str,
    user_id: int,
    workspace_id: int,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """
    Complete tool-routing pipeline.

    Flow:

        User question
              ↓
        Detect tool
              ↓
        Build arguments
              ↓
        Create ToolContext
              ↓
        Tool Registry
              ↓
        Execute tool

    Returns None when the request is not a tool request.
    """

    tool_name = detect_tool(question)

    if tool_name is None:
        return None

    arguments = build_tool_arguments(
        tool_name=tool_name,
        question=question,
    )

    result = execute_chat_tool(
        tool_name=tool_name,
        arguments=arguments,
        user_id=user_id,
        workspace_id=workspace_id,
        metadata=metadata,
    )

    return {
        "tool": tool_name,
        "arguments": arguments,
        "result": result,
    }
