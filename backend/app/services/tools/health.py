from typing import Any

from app.services.tools.base import (
    BaseTool,
    ToolContext,
)


class HealthTool(BaseTool):

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
