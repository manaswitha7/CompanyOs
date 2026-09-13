from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.database.database import SessionLocal
from app.models.document import Document

from app.services.structured_data.service import (
    structured_data_service,
)


router = APIRouter(
    prefix="/structured-data",
    tags=["Structured Data"],
)


# ============================================================
# REQUEST MODELS
# ============================================================


class PreviewRequest(BaseModel):

    document_id: int

    sheet_name: str | None = None

    limit: int = Field(
        default=20,
        ge=1,
        le=100,
    )


class QueryRequest(BaseModel):

    document_id: int

    sheet_name: str

    column: str

    value: str


# ============================================================
# GET SCHEMA
# ============================================================


@router.get("/{document_id}/schema")
def get_schema(
    document_id: int,
):

    db = SessionLocal()

    try:

        document = (
            db.query(Document)
            .filter(
                Document.id == document_id
            )
            .first()
        )

        if not document:

            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )

        if document.file_type.lower() not in {
            "csv",
            "xlsx",
            "xls",
        }:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Document is not a supported "
                    "structured data format"
                ),
            )

        return structured_data_service.get_schema(
            storage_key=document.storage_key,
            file_type=document.file_type,
        )

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    finally:

        db.close()


# ============================================================
# PREVIEW
# ============================================================


@router.post("/preview")
def preview(
    request: PreviewRequest,
):

    db = SessionLocal()

    try:

        document = (
            db.query(Document)
            .filter(
                Document.id == request.document_id
            )
            .first()
        )

        if not document:

            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )

        return structured_data_service.preview(
            storage_key=document.storage_key,
            file_type=document.file_type,
            sheet_name=request.sheet_name,
            limit=request.limit,
        )

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    finally:

        db.close()


# ============================================================
# QUERY
# ============================================================


@router.post("/query")
def query_structured_data(
    request: QueryRequest,
):

    db = SessionLocal()

    try:

        document = (
            db.query(Document)
            .filter(
                Document.id == request.document_id
            )
            .first()
        )

        if not document:

            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )

        return structured_data_service.query(
            storage_key=document.storage_key,
            file_type=document.file_type,
            sheet_name=request.sheet_name,
            column=request.column,
            value=request.value,
        )

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    finally:

        db.close()
