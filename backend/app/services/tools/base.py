from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolContext:
    """
    Runtime context available to Company OS tools.
    """

    workspace_id: int | None = None
    user_id: int | None = None
    db: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseTool(ABC):
    """
    Base interface for all Company OS tools.

    Every tool provides:
    - unique name
    - description
    - category
    - input schema
    - execution method
    """

    name: str
    description: str
    category: str = "general"

    @property
    @abstractmethod
    def input_schema(self) -> dict[str, Any]:
        """
        JSON-schema-like description of tool inputs.
        """
        raise NotImplementedError

    @abstractmethod
    def execute(
        self,
        context: ToolContext,
        arguments: dict[str, Any],
    ) -> Any:
        """
        Execute the tool.
        """
        raise NotImplementedError

    def definition(self) -> dict[str, Any]:
        """
        Return an LLM/MCP-compatible tool definition.
        """

        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "input_schema": self.input_schema,
        }

    # Backwards-compatible alias used by the registry.
    def schema(self) -> dict[str, Any]:
        return self.definition()
