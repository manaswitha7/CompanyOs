from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.document import Document
from app.models.document_source import DocumentSource
from app.models.user import User
from app.services.permissions.dependencies import require_permission
from app.services.permissions.roles import Permission


router = APIRouter(
    prefix="/lineage",
    tags=["Lineage"],
)


@router.get("/documents/{document_id}")
def get_document_lineage(
    document_id: int,
    current_user: User = Depends(
        require_permission(
            Permission.DOCUMENTS_READ
        )
    ),
    db: Session = Depends(get_db),
):
    if current_user.workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to a workspace.",
        )

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.workspace_id
            == current_user.workspace_id,
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    sources = (
        db.query(DocumentSource)
        .filter(
            DocumentSource.document_id
            == document.id
        )
        .all()
    )

    return {
        "document": {
            "id": document.id,
            "filename": document.filename,
            "storage_key": document.storage_key,
            "status": document.status,
        },
        "sources": [
            {
                "id": source.id,
                "source_type": source.source_type,
                "source_name": source.source_name,
                "source_uri": source.source_uri,
                "ingestion_method": source.ingestion_method,
                "created_at": source.created_at,
            }
            for source in sources
        ],
    }
