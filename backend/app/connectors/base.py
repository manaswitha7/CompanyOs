from abc import ABC, abstractmethod
from typing import Any


class BaseConnector(ABC):
    """
    Base interface for all Company OS external connectors.

    Every connector such as GitHub, Slack, Google Drive,
    Jira, or Confluence should implement this interface.
    """

    name: str = ""
    display_name: str = ""

    @abstractmethod
    def connect(self, credentials: dict[str, Any]) -> dict[str, Any]:
        """
        Establish a connection to the external system.
        """
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> dict[str, Any]:
        """
        Disconnect from the external system.
        """
        raise NotImplementedError

    @abstractmethod
    def test_connection(self) -> dict[str, Any]:
        """
        Verify that the connection is working.
        """
        raise NotImplementedError

    @abstractmethod
    def fetch(self, **kwargs: Any) -> list[dict[str, Any]]:
        """
        Fetch data from the external system.
        """
        raise NotImplementedError

    @abstractmethod
    def normalize(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Convert external records into the normalized
        Company OS representation.
        """
        raise NotImplementedError
