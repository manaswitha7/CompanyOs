from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.database.database import SessionLocal
from app.services.entity_resolution import (
    entity_resolution_service,
)


router = APIRouter(
    prefix="/entity-resolution",
    tags=["Entity Resolution"],
)


class ResolveEntityRequest(BaseModel):
    workspace_id: int
    provider: str

    external_id: str | None = None
    external_email: str | None = None
    external_name: str | None = None
    connector_id: int | None = None


@router.post("/resolve")
def resolve_entity(
    request: ResolveEntityRequest,
) -> dict[str, Any]:

    db = SessionLocal()

    try:
        result = entity_resolution_service.resolve(
            db=db,
            workspace_id=request.workspace_id,
            provider=request.provider,
            external_id=request.external_id,
            external_email=request.external_email,
            external_name=request.external_name,
            connector_id=request.connector_id,
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    finally:
        db.close()
