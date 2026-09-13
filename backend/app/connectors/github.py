from typing import Any

import requests

from app.connectors.base import BaseConnector


class GitHubConnector(BaseConnector):
    name = "github"
    display_name = "GitHub"

    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.credentials: dict[str, Any] = {}
        self.connected = False

    # ============================================================
    # CONNECT
    # ============================================================

    def connect(
        self,
        credentials: dict[str, Any],
    ) -> dict[str, Any]:

        token = credentials.get("token")

        if not token:
            raise ValueError(
                "GitHub token is required."
            )

        self.credentials = credentials
        self.connected = True

        return {
            "status": "connected",
            "connector": self.name,
            "message": "GitHub connector connected successfully",
        }

    # ============================================================
    # DISCONNECT
    # ============================================================

    def disconnect(self) -> dict[str, Any]:

        self.credentials = {}
        self.connected = False

        return {
            "status": "disconnected",
            "connector": self.name,
        }

    # ============================================================
    # TEST CONNECTION
    # ============================================================

    def test_connection(self) -> dict[str, Any]:

        if not self.connected:
            return {
                "connected": False,
                "connector": self.name,
                "status": "not_connected",
            }

        try:

            response = requests.get(
                f"{self.BASE_URL}/user",
                headers=self._headers(),
                timeout=15,
            )

            response.raise_for_status()

            user = response.json()

            return {
                "connected": True,
                "connector": self.name,
                "status": "healthy",
                "github_user": user.get("login"),
            }

        except requests.RequestException as exc:

            return {
                "connected": False,
                "connector": self.name,
                "status": "unhealthy",
                "error": str(exc),
            }

    # ============================================================
    # HEADERS
    # ============================================================

    def _headers(self) -> dict[str, str]:

        token = self.credentials.get("token")

        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    # ============================================================
    # FETCH
    # ============================================================

    def fetch(
        self,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:

        if not self.connected:
            raise RuntimeError(
                "GitHub connector is not connected"
            )

        repository = kwargs.get("repository")

        if not repository:
            raise ValueError(
                "repository is required. "
                "Example: owner/repository"
            )

        state = kwargs.get(
            "state",
            "open",
        )

        limit = int(
            kwargs.get(
                "limit",
                10,
            )
        )

        if limit < 1:
            limit = 1

        if limit > 100:
            limit = 100

        # --------------------------------------------------------
        # Fetch repository issues
        # --------------------------------------------------------

        url = (
            f"{self.BASE_URL}/repos/"
            f"{repository}/issues"
        )

        params = {
            "state": state,
            "per_page": limit,
        }

        try:

            response = requests.get(
                url,
                headers=self._headers(),
                params=params,
                timeout=20,
            )

            response.raise_for_status()

        except requests.HTTPError as exc:

            detail = response.text

            raise RuntimeError(
                f"GitHub API error: "
                f"{response.status_code} - {detail}"
            ) from exc

        except requests.RequestException as exc:

            raise RuntimeError(
                f"Failed to connect to GitHub: {exc}"
            ) from exc

        issues = response.json()

        # --------------------------------------------------------
        # Normalize raw GitHub response
        # --------------------------------------------------------

        records = []

        for issue in issues:

            # GitHub's /issues endpoint also returns
            # pull requests. Keep that information.

            is_pull_request = (
                "pull_request" in issue
            )

            records.append(
                {
                    "id": issue.get("id"),
                    "number": issue.get("number"),
                    "name": issue.get("title"),
                    "title": issue.get("title"),
                    "description": issue.get(
                        "body"
                    ) or "",
                    "text": issue.get(
                        "body"
                    ) or "",
                    "state": issue.get("state"),
                    "url": issue.get(
                        "html_url"
                    ),
                    "author": (
                        issue.get("user") or {}
                    ).get("login"),
                    "created_at": issue.get(
                        "created_at"
                    ),
                    "updated_at": issue.get(
                        "updated_at"
                    ),
                    "type": (
                        "pull_request"
                        if is_pull_request
                        else "issue"
                    ),
                    "labels": [
                        label.get("name")
                        for label in (
                            issue.get("labels")
                            or []
                        )
                    ],
                    "repository": repository,
                }
            )

        return records

    # ============================================================
    # NORMALIZE
    # ============================================================

    def normalize(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        return [
            {
                "source": "github",
                "source_type": record.get(
                    "type",
                    "issue",
                ),
                "external_id": record.get(
                    "id"
                ),
                "title": record.get(
                    "title"
                ),
                "content": record.get(
                    "description",
                    "",
                ),
                "metadata": record,
            }
            for record in records
        ]
