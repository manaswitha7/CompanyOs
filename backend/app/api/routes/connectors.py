from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.services.auth.dependencies import get_current_user
from app.services.connectors.service import connector_service
from app.services.connectors.github_ingestion import (
    github_ingestion_service,
)
from app.services.permissions.dependencies import (
    require_permission,
)
from app.services.permissions.roles import Permission


router = APIRouter(
    prefix="/connectors",
    tags=["Connectors"],
)


# ============================================================
# REQUEST MODELS
# ============================================================


class ConnectorCredentials(BaseModel):
    credentials: dict[str, Any] = Field(
        default_factory=dict
    )


class FetchRequest(BaseModel):
    credentials: dict[str, Any] = Field(
        default_factory=dict
    )

    options: dict[str, Any] = Field(
        default_factory=dict
    )


class NormalizeRequest(BaseModel):
    records: list[dict[str, Any]] = Field(
        default_factory=list
    )


class GitHubIngestRequest(BaseModel):
    credentials: dict[str, Any] = Field(
        default_factory=dict
    )

    repository: str = Field(
        ...,
        description="GitHub repository in owner/repository format",
    )

    state: str = Field(
        default="open",
        description="Issue state: open, closed, or all",
    )

    limit: int = Field(
        default=50,
        ge=1,
        le=100,
    )


# ============================================================
# LIST CONNECTORS
# ============================================================


@router.get("")
def list_connectors():

    try:

        return {
            "connectors": (
                connector_service
                .list_registered_connectors()
            )
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


# ============================================================
# CONNECT
# ============================================================


@router.post("/{connector_name}/connect")
def connect_connector(
    connector_name: str,
    request: ConnectorCredentials,
):

    try:

        result = connector_service.connect(
            connector_name,
            request.credentials,
        )

        return {
            "connector": connector_name,
            **result,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


# ============================================================
# TEST CONNECTION
# ============================================================


@router.post("/{connector_name}/test")
def test_connector(
    connector_name: str,
    request: ConnectorCredentials | None = None,
):

    try:

        credentials = (
            request.credentials
            if request
            else None
        )

        result = connector_service.test_connection(
            connector_name,
            credentials,
        )

        return {
            "connector": connector_name,
            **result,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


# ============================================================
# FETCH
# ============================================================


@router.post("/{connector_name}/fetch")
def fetch_connector_data(
    connector_name: str,
    request: FetchRequest,
):

    try:

        records = connector_service.fetch(
            connector_name,
            request.credentials,
            **request.options,
        )

        return {
            "connector": connector_name,
            "count": len(records),
            "records": records,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


# ============================================================
# NORMALIZE
# ============================================================


@router.post("/{connector_name}/normalize")
def normalize_connector_data(
    connector_name: str,
    request: NormalizeRequest,
):

    try:

        records = connector_service.normalize(
            connector_name,
            request.records,
        )

        return {
            "connector": connector_name,
            "count": len(records),
            "records": records,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


# ============================================================
# GITHUB → RAG INGESTION
# ============================================================


@router.post("/github/ingest")
def ingest_github(
    request: GitHubIngestRequest,
    current_user: User = Depends(
        require_permission(
            Permission.CHAT_USE
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Fetch GitHub issues/PRs and ingest them into
    Company OS RAG.

    Flow:

        GitHub
          ↓
        Fetch
          ↓
        Normalize
          ↓
        Document
          ↓
        Embeddings
          ↓
        pgvector
          ↓
        RAG
    """

    if current_user.workspace_id is None:

        raise HTTPException(
            status_code=400,
            detail=(
                "User is not assigned "
                "to a workspace."
            ),
        )

    if not request.credentials.get("token"):

        raise HTTPException(
            status_code=400,
            detail="GitHub token is required.",
        )

    try:

        result = github_ingestion_service.ingest(
            workspace_id=current_user.workspace_id,
            owner_id=current_user.id,
            credentials=request.credentials,
            repository=request.repository,
            state=request.state,
            limit=request.limit,
        )

        return {
            "success": True,
            **result,
        }

    except ValueError as exc:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "GitHub ingestion failed: "
                f"{str(exc)}"
            ),
        ) from exc


# ============================================================
# DISCONNECT
# ============================================================


@router.delete("/{connector_name}")
def disconnect_connector(
    connector_name: str,
):

    try:

        result = connector_service.disconnect(
            connector_name
        )

        return {
            "connector": connector_name,
            **result,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc
