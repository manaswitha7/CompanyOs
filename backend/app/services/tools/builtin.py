from typing import Any

from app.services.tools.base import (
    BaseTool,
    ToolContext,
)


class HealthCheckTool(BaseTool):

    name = "system_health"
    description = "Check Company OS backend health."
    category = "system"

    @property
    def input_schema(self) -> dict[str, Any]:

        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    def execute(
        self,
        context: ToolContext,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:

        return {
            "status": "healthy",
            "service": "company-os",
        }


class EchoTool(BaseTool):

    name = "echo"
    description = "Return the supplied message."
    category = "utility"

    @property
    def input_schema(self) -> dict[str, Any]:

        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Message to echo",
                }
            },
            "required": ["message"],
        }

    def execute(
        self,
        context: ToolContext,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:

        message = arguments.get(
            "message",
            "",
        )

        return {
            "message": message,
        }


class ListAvailableToolsTool(BaseTool):

    name = "list_tools"
    description = (
        "List tools available to the Company OS agent."
    )
    category = "system"

    @property
    def input_schema(self) -> dict[str, Any]:

        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    def execute(
        self,
        context: ToolContext,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:

        from app.services.tools.registry import tool_registry

        return {
            "tools": tool_registry.list_tools()
        }
