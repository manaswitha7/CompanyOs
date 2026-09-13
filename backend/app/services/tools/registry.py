from typing import Any

from app.services.tools.base import (
    BaseTool,
    ToolContext,
)


class ToolRegistry:
    """
    Central registry for Company OS tools.

    The registry is responsible for:
    - registering tools
    - retrieving tools
    - listing tool definitions
    - executing tools
    """

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    # ========================================================
    # REGISTER
    # ========================================================

    def register(self, tool: BaseTool) -> None:
        """
        Register a tool instance.
        """

        if not isinstance(tool, BaseTool):
            raise TypeError(
                "Only BaseTool instances can be registered."
            )

        if not tool.name:
            raise ValueError(
                "Tool must have a name."
            )

        if tool.name in self._tools:
            raise ValueError(
                f"Tool '{tool.name}' is already registered."
            )

        self._tools[tool.name] = tool

    # ========================================================
    # GET
    # ========================================================

    def get(
        self,
        name: str,
    ) -> BaseTool | None:
        """
        Retrieve a registered tool by name.
        """

        return self._tools.get(name)

    # ========================================================
    # LIST
    # ========================================================

    def list_tools(self) -> list[dict[str, Any]]:
        """
        Return definitions of all registered tools.

        These definitions can be supplied to:
        - LLMs
        - MCP
        - agent orchestration
        - frontend tool discovery
        """

        return [
            tool.definition()
            for tool in self._tools.values()
        ]

    # ========================================================
    # EXECUTE
    # ========================================================

    def execute(
        self,
        name: str,
        context: ToolContext,
        arguments: dict[str, Any] | None = None,
    ) -> Any:
        """
        Execute a registered tool.
        """

        tool = self.get(name)

        if tool is None:
            raise ValueError(
                f"Tool '{name}' is not registered."
            )

        if arguments is None:
            arguments = {}

        return tool.execute(
            context=context,
            arguments=arguments,
        )

    # ========================================================
    # EXISTS
    # ========================================================

    def exists(
        self,
        name: str,
    ) -> bool:
        """
        Check whether a tool is registered.
        """

        return name in self._tools

    # ========================================================
    # COUNT
    # ========================================================

    def count(self) -> int:
        """
        Return number of registered tools.
        """

        return len(self._tools)


tool_registry = ToolRegistry()
