from typing import Any

from app.connectors.base import BaseConnector


class SlackConnector(BaseConnector):
    name = "slack"
    display_name = "Slack"

    def __init__(self):
        self.credentials: dict[str, Any] = {}
        self.connected = False

    def connect(self, credentials: dict[str, Any]) -> dict[str, Any]:
        self.credentials = credentials
        self.connected = True

        return {
            "status": "connected",
            "connector": self.name,
            "message": "Slack connector connected successfully",
        }

    def disconnect(self) -> dict[str, Any]:
        self.credentials = {}
        self.connected = False

        return {
            "status": "disconnected",
            "connector": self.name,
        }

    def test_connection(self) -> dict[str, Any]:
        return {
            "connected": self.connected,
            "connector": self.name,
            "status": "healthy" if self.connected else "not_connected",
        }

    def fetch(self, **kwargs: Any) -> list[dict[str, Any]]:
        if not self.connected:
            raise RuntimeError("Slack connector is not connected")

        return []

    def normalize(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        return [
            {
                "source": "slack",
                "source_type": "message",
                "external_id": record.get("id"),
                "title": record.get("title"),
                "content": record.get("text", ""),
                "metadata": record,
            }
            for record in records
        ]
