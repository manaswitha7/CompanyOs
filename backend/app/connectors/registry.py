from typing import Type

from app.connectors.base import BaseConnector
from app.connectors.slack import SlackConnector
from app.connectors.github import GitHubConnector
from app.connectors.google_drive import GoogleDriveConnector
from app.connectors.email import EmailConnector
from app.connectors.confluence import ConfluenceConnector


class ConnectorRegistry:
    def __init__(self):
        self._connectors: dict[str, Type[BaseConnector]] = {}

    def register(
        self,
        connector_class: Type[BaseConnector],
    ) -> None:
        self._connectors[connector_class.name] = connector_class

    def get(
        self,
        name: str,
    ) -> Type[BaseConnector] | None:
        return self._connectors.get(name)

    def list(self) -> list[Type[BaseConnector]]:
        return list(self._connectors.values())


connector_registry = ConnectorRegistry()


connector_registry.register(SlackConnector)
connector_registry.register(GitHubConnector)
connector_registry.register(GoogleDriveConnector)

connector_registry.register(EmailConnector)
connector_registry.register(ConfluenceConnector)
