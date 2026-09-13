from fastapi import APIRouter, HTTPException

from app.database.database import SessionLocal
from app.models.document import Document

from app.services.queue.redis_queue import (
    enqueue_ingestion,
)


router = APIRouter(
    prefix="/ingestion",
    tags=["Ingestion"],
)


@router.post("/process/{document_id}")
def process_document(
    document_id: int,
):
    """
    Queue a document for asynchronous processing.
    """

    db = SessionLocal()

    try:

        # ---------------------------------------------
        # 1. Verify document exists
        # ---------------------------------------------

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

        # ---------------------------------------------
        # 2. Add job to Redis
        # ---------------------------------------------

        enqueue_ingestion(
            document_id
        )

        # ---------------------------------------------
        # 3. Return immediately
        # ---------------------------------------------

        return {
            "message": (
                "Document ingestion queued"
            ),
            "document_id": document.id,
            "filename": document.filename,
            "status": "queued",
        }

    finally:

        db.close()
