from typing import Any

from app.connectors.base import BaseConnector
from app.connectors.registry import connector_registry


@connector_registry.register
class MockConnector(BaseConnector):

    name = "mock"
    display_name = "Mock Connector"

    def __init__(self):
        self.connected = False
        self.credentials: dict[str, Any] = {}

    def connect(
        self,
        credentials: dict[str, Any],
    ) -> dict[str, Any]:

        self.credentials = credentials
        self.connected = True

        return {
            "success": True,
            "status": "connected",
            "message": "Mock connector connected successfully",
        }

    def disconnect(self) -> dict[str, Any]:

        self.connected = False
        self.credentials = {}

        return {
            "success": True,
            "status": "disconnected",
        }

    def test_connection(self) -> dict[str, Any]:

        return {
            "success": self.connected,
            "status": "connected"
            if self.connected
            else "disconnected",
        }

    def fetch(
        self,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "Connector is not connected"
            )

        return [
            {
                "id": "mock-1",
                "title": "Mock record",
                "content": "Example Company OS connector data",
                "source": "mock",
            }
        ]

    def normalize(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        return [
            {
                "external_id": record.get("id"),
                "title": record.get("title"),
                "content": record.get("content"),
                "source_type": self.name,
            }
            for record in records
        ]
