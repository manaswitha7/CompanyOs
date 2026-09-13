import os
from typing import Any

from dotenv import load_dotenv

from app.services.tools.base import (
    BaseTool,
    ToolContext,
)

from app.connectors.registry import (
    connector_registry,
)
from app.services.tools.registry import tool_registry

load_dotenv()


class GitHubFetchTool(BaseTool):
    """
    Company OS tool for fetching data from GitHub.
    """

    name = "github_fetch"

    description = (
        "Fetch data from a connected GitHub repository."
    )

    category = "connector"

    @property
    def input_schema(self) -> dict[str, Any]:

        return {
            "type": "object",

            "properties": {

                "repository": {
                    "type": "string",
                    "description": (
                        "GitHub repository in "
                        "owner/repository format."
                    ),
                },

                "state": {
                    "type": "string",
                    "description": (
                        "Issue state: open, closed, or all."
                    ),
                    "enum": [
                        "open",
                        "closed",
                        "all",
                    ],
                },

                "limit": {
                    "type": "integer",
                    "description": (
                        "Maximum number of records to fetch."
                    ),
                },
            },

            "required": [
                "repository",
            ],
        }

    def execute(
        self,
        context: ToolContext,
        arguments: dict[str, Any],
    ) -> Any:

        # ==================================================
        # 1. Read repository
        # ==================================================

        repository = arguments.get(
            "repository"
        )

        if not repository:
            raise ValueError(
                "repository is required."
            )

        # ==================================================
        # 2. Read optional arguments
        # ==================================================

        state = arguments.get(
            "state",
            "open",
        )

        limit = arguments.get(
            "limit",
            10,
        )

        # ==================================================
        # 3. Validate limit
        # ==================================================

        if not isinstance(limit, int):
            raise ValueError(
                "limit must be an integer."
            )

        if limit < 1:
            raise ValueError(
                "limit must be greater than 0."
            )

        # ==================================================
        # 4. Get GitHub connector
        # ==================================================

        connector_class = (
            connector_registry.get("github")
        )

        if connector_class is None:
            raise ValueError(
                "GitHub connector is not registered."
            )

        # ==================================================
        # 5. Create connector instance
        # ==================================================

        connector = connector_class()

        # ==================================================
        # 6. Resolve credentials
        #
        # Priority:
        #
        # 1. ToolContext credentials
        # 2. GITHUB_TOKEN environment variable
        # ==================================================

        credentials = context.metadata.get(
            "github_credentials"
        )

        if not credentials:

            token = os.getenv(
                "GITHUB_TOKEN"
            )

            if token:

                credentials = {
                    "token": token
                }

        # ==================================================
        # 7. Make sure credentials exist
        # ==================================================

        if not credentials:

            raise ValueError(
                "GitHub credentials are not configured."
            )

        # ==================================================
        # 8. Connect to GitHub
        # ==================================================

        connector.connect(
            credentials
        )

        # ==================================================
        # 9. Fetch GitHub records
        # ==================================================

        records = connector.fetch(
            repository=repository,
            state=state,
            limit=limit,
        )

        # ==================================================
        # 10. Return normalized tool result
        # ==================================================

        return {
            "connector": "github",
            "repository": repository,
            "state": state,
            "count": len(records),
            "records": records,
        }


# ==========================================================
# TOOL REGISTRATION
# ==========================================================

def register_connector_tools():

    tools = [
        GitHubFetchTool(),
    ]

    for tool in tools:

        if not tool_registry.exists(
            tool.name
        ):

            tool_registry.register(
                tool
            )
