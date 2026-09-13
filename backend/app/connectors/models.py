from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConnectorInfo:
    """
    Metadata describing a connector.
    """

    name: str
    display_name: str
    description: str = ""
    category: str = "external"
    capabilities: list[str] = field(default_factory=list)
    configured: bool = False
    connected: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "category": self.category,
            "capabilities": self.capabilities,
            "configured": self.configured,
            "connected": self.connected,
        }
