from typing import Any

from app.connectors.base import BaseConnector


class GoogleDriveConnector(BaseConnector):
    name = "google_drive"
    display_name = "Google Drive"

    def __init__(self):
        self.credentials: dict[str, Any] = {}
        self.connected = False

    def connect(self, credentials: dict[str, Any]) -> dict[str, Any]:
        self.credentials = credentials
        self.connected = True

        return {
            "status": "connected",
            "connector": self.name,
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
            raise RuntimeError("Google Drive connector is not connected")

        return []

    def normalize(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        return [
            {
                "source": "google_drive",
                "source_type": "document",
                "external_id": record.get("id"),
                "title": record.get("name"),
                "content": record.get("content", ""),
                "metadata": record,
            }
            for record in records
        ]
