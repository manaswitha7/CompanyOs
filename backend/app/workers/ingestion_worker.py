import logging
import time

from app.database.database import SessionLocal
from app.models.document import Document

from app.services.queue.redis_queue import (
    dequeue_ingestion,
)

from app.services.ingestion.processor import (
    process_document,
)


logging.basicConfig(
    level=logging.INFO,
)

logger = logging.getLogger(
    "companyos.ingestion_worker"
)


def update_document_status(
    document_id: int,
    status: str,
):
    """
    Update the processing status of a document.
    """

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
            logger.warning(
                "Document %s not found while updating status to %s",
                document_id,
                status,
            )
            return

        document.status = status

        db.commit()

        logger.info(
            "Document %s status -> %s",
            document_id,
            status,
        )

    except Exception:
        db.rollback()

        logger.exception(
            "Failed to update status for document %s",
            document_id,
        )

    finally:
        db.close()


def run_worker():
    """
    Continuously process ingestion jobs
    from Redis.
    """

    logger.info(
        "Company OS ingestion worker started"
    )

    while True:

        try:

            job = dequeue_ingestion()

            if not job:
                continue

            document_id = job[
                "document_id"
            ]

            logger.info(
                "Processing document %s",
                document_id,
            )

            # -----------------------------------------
            # Mark as processing
            # -----------------------------------------

            update_document_status(
                document_id,
                "processing",
            )

            try:

                # -----------------------------------------
                # Process document
                # -----------------------------------------

                result = process_document(
                    document_id
                )

                # -----------------------------------------
                # Mark as completed
                # -----------------------------------------

                update_document_status(
                    document_id,
                    "completed",
                )

                logger.info(
                    "Document %s processed successfully: %s",
                    document_id,
                    result,
                )

            except Exception:

                # -----------------------------------------
                # Mark as failed
                # -----------------------------------------

                update_document_status(
                    document_id,
                    "failed",
                )

                logger.exception(
                    "Failed to process document %s",
                    document_id,
                )

        except KeyboardInterrupt:

            logger.info(
                "Ingestion worker shutting down"
            )

            break

        except Exception:

            logger.exception(
                "Unexpected worker error"
            )

            # Prevent a tight failure loop
            time.sleep(2)


if __name__ == "__main__":

    run_worker()
