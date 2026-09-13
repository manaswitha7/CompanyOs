from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.models.document_permission import DocumentPermission
from app.models.user import User

from app.services.audit.service import create_audit_log
from app.services.permissions.dependencies import require_permission
from app.services.permissions.document_access import (
    can_delete_document,
    can_read_document,
)
from app.services.permissions.roles import Permission
from app.services.queue.redis_queue import enqueue_ingestion
from app.services.storage.minio import (
    delete_file,
    upload_file,
)

from app.services.auth.dependencies import get_current_user


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


# ============================================================
# ALLOWED FILE TYPES
# ============================================================

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "text/plain": "txt",
    "text/markdown": "md",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/x-yaml": "yaml",
    "text/yaml": "yaml",
    "text/csv": "csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/vnd.ms-excel": "xls",
}


# ============================================================
# FALLBACK EXTENSIONS
# ============================================================

ALLOWED_EXTENSIONS = {
    ".pdf": "pdf",
    ".txt": "txt",
    ".md": "md",
    ".markdown": "md",
    ".docx": "docx",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".csv": "csv",
    ".xlsx": "xlsx",
    ".xls": "xls",
}


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(
        require_permission(
            Permission.DOCUMENTS_CREATE
        )
    ),
):
    """
    Upload a supported document.

    Supported formats:
        PDF
        TXT
        Markdown
        DOCX
        YAML
        CSV
        XLSX
        XLS

    The document is:
        1. Uploaded to MinIO
        2. Registered in PostgreSQL
        3. Assigned to the user's workspace
        4. Given owner read permission
        5. Audited
        6. Queued for ingestion
    """

    # ========================================================
    # 1. VALIDATE WORKSPACE
    # ========================================================

    if current_user.workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to a workspace.",
        )

    # ========================================================
    # 2. VALIDATE FILE NAME
    # ========================================================

    filename = file.filename or "unknown"

    if "." not in filename:
        raise HTTPException(
            status_code=400,
            detail="File must have a supported extension.",
        )

    extension_from_filename = (
        "."
        + filename.rsplit(".", 1)[-1].lower()
    )

    # ========================================================
    # 3. VALIDATE FILE TYPE
    # ========================================================

    extension = ALLOWED_TYPES.get(
        file.content_type
    )

    if extension is None:
        extension = ALLOWED_EXTENSIONS.get(
            extension_from_filename
        )

    if extension is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Supported formats: "
                "PDF, TXT, MD, DOCX, YAML, "
                "YML, CSV, XLSX and XLS."
            ),
        )

    # ========================================================
    # 4. GENERATE UNIQUE STORAGE KEY
    # ========================================================

    object_name = (
        f"documents/{uuid4()}.{extension}"
    )

    db: Session = SessionLocal()

    try:

        # ====================================================
        # 5. UPLOAD ORIGINAL FILE TO MINIO
        # ====================================================

        await file.seek(0)

        upload_file(
            file.file,
            object_name,
            file.content_type
            or "application/octet-stream",
        )

        # ====================================================
        # 6. CREATE DOCUMENT
        # ====================================================

        document = Document(
            workspace_id=current_user.workspace_id,
            owner_id=current_user.id,
            filename=filename,
            file_type=extension,
            storage_key=object_name,
        )

        db.add(document)

        # Get document ID
        db.flush()

        # ====================================================
        # 7. GIVE OWNER EXPLICIT READ PERMISSION
        # ====================================================

        document_permission = DocumentPermission(
            document_id=document.id,
            user_id=current_user.id,
            permission="read",
        )

        db.add(document_permission)

        # ====================================================
        # 8. CREATE AUDIT RECORD
        # ====================================================

        create_audit_log(
            db,
            workspace_id=current_user.workspace_id,
            user_id=current_user.id,
            action="DOCUMENT_UPLOADED",
            resource_type="document",
            resource_id=document.id,
            details={
                "filename": document.filename,
                "file_type": document.file_type,
                "storage_key": document.storage_key,
                "owner_id": current_user.id,
                "content_type": file.content_type,
            },
        )

        # ====================================================
        # 9. COMMIT
        # ====================================================

        db.commit()

        db.refresh(document)

        # ====================================================
        # 10. QUEUE INGESTION
        # ====================================================

        enqueue_ingestion(
            document.id
        )

        # ====================================================
        # 11. RETURN
        # ====================================================

        return {
            "message": "Document uploaded successfully",
            "document_id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "content_type": file.content_type,
            "storage_key": document.storage_key,
            "workspace_id": document.workspace_id,
            "ingestion_status": "queued",
        }

    except Exception:

        db.rollback()

        # If database processing fails after MinIO upload,
        # remove the uploaded object.

        try:
            delete_file(object_name)
        except Exception:
            pass

        raise

    finally:
        db.close()


# ============================================================
# LIST DOCUMENTS
# ============================================================

@router.get("")
def list_documents(
    current_user: User = Depends(
        require_permission(
            Permission.DOCUMENTS_READ
        )
    ),
):
    """
    List documents the authenticated user can read.
    """

    if current_user.workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to a workspace.",
        )

    db: Session = SessionLocal()

    try:

        documents = (
            db.query(Document)
            .filter(
                Document.workspace_id
                == current_user.workspace_id
            )
            .order_by(
                Document.created_at.desc()
            )
            .all()
        )

        accessible_documents = []

        for document in documents:

            if can_read_document(
                db=db,
                user_id=current_user.id,
                role=current_user.role,
                document_id=document.id,
            ):
                accessible_documents.append(
                    document
                )

        return {
            "documents": [
                {
                    "document_id": document.id,
                    "filename": document.filename,
                    "file_type": document.file_type,
                    "status": document.status,
                    "workspace_id": document.workspace_id,
                    "created_at": document.created_at,
                }
                for document in accessible_documents
            ]
        }

    finally:
        db.close()


# ============================================================
# GET SINGLE DOCUMENT
# ============================================================

@router.get("/{document_id}")
def get_document(
    document_id: int,
    current_user: User = Depends(
        require_permission(
            Permission.DOCUMENTS_READ
        )
    ),
):
    """
    Get a single document.
    """

    if current_user.workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to a workspace.",
        )

    db: Session = SessionLocal()

    try:

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

        if not can_read_document(
            db=db,
            user_id=current_user.id,
            role=current_user.role,
            document_id=document.id,
        ):
            raise HTTPException(
                status_code=403,
                detail=(
                    "You do not have permission "
                    "to access this document."
                ),
            )

        return {
            "document_id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "status": document.status,
            "workspace_id": document.workspace_id,
            "created_at": document.created_at,
        }

    finally:
        db.close()


# ============================================================
# DELETE FAILED DOCUMENT
# ============================================================

@router.delete("/{document_id}/failed")
def delete_failed_document(
    document_id: int,
    current_user: User = Depends(
        require_permission(
            Permission.DOCUMENTS_READ
        )
    ),
):
    """
    Delete a failed document.

    IMPORTANT:
    This endpoint intentionally does NOT require
    Permission.DOCUMENTS_DELETE.

    Reason:
    A member should be able to clean up documents
    that failed during ingestion.

    Security:
        - User must be authenticated.
        - User must belong to a workspace.
        - Document must belong to that workspace.
        - Document must have status='failed'.
        - MinIO object is deleted.
        - Document chunks are deleted.
        - Document permissions are deleted.
        - Document is deleted.
        - Audit event is recorded.
    """

    # ========================================================
    # 1. VALIDATE WORKSPACE
    # ========================================================

    if current_user.workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to a workspace.",
        )

    db: Session = SessionLocal()

    try:

        # ====================================================
        # 2. FIND DOCUMENT IN USER WORKSPACE
        # ====================================================

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

        # ====================================================
        # 3. ONLY FAILED DOCUMENTS
        # ====================================================

        if document.status != "failed":
            raise HTTPException(
                status_code=400,
                detail=(
                    "Only failed documents can be "
                    "deleted using this endpoint."
                ),
            )

        filename = document.filename
        file_type = document.file_type
        storage_key = document.storage_key

        # ====================================================
        # 4. DELETE MINIO FILE
        # ====================================================

        try:

            delete_file(
                storage_key
            )

        except Exception as exc:

            raise HTTPException(
                status_code=500,
                detail=(
                    "Failed to delete stored file: "
                    f"{exc}"
                ),
            )

        # ====================================================
        # 5. DELETE DOCUMENT CHUNKS
        # ====================================================

        db.query(
            DocumentChunk
        ).filter(
            DocumentChunk.document_id
            == document.id
        ).delete(
            synchronize_session=False
        )

        # ====================================================
        # 6. DELETE DOCUMENT PERMISSIONS
        # ====================================================

        db.query(
            DocumentPermission
        ).filter(
            DocumentPermission.document_id
            == document.id
        ).delete(
            synchronize_session=False
        )

        # ====================================================
        # 7. CREATE AUDIT LOG
        # ====================================================

        create_audit_log(
            db,
            workspace_id=current_user.workspace_id,
            user_id=current_user.id,
            action="FAILED_DOCUMENT_DELETED",
            resource_type="document",
            resource_id=document.id,
            details={
                "filename": filename,
                "file_type": file_type,
                "storage_key": storage_key,
                "previous_status": "failed",
            },
        )

        # ====================================================
        # 8. DELETE DOCUMENT
        # ====================================================

        db.delete(document)

        db.commit()

        # ====================================================
        # 9. RETURN
        # ====================================================

        return {
            "message": (
                "Failed document deleted successfully"
            ),
            "document_id": document_id,
        }

    except HTTPException:

        db.rollback()
        raise

    except Exception:

        db.rollback()
        raise

    finally:
        db.close()


# ============================================================
# DELETE DOCUMENT
# ============================================================

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Delete a document.

    Rules:

    1. Users must belong to a workspace.
    2. Members can delete ONLY failed documents.
    3. Other users must satisfy the normal document
       deletion permission/ownership rules.
    4. The MinIO file, chunks, permissions and document
       record are removed.
    """

    # --------------------------------------------------------
    # Workspace validation
    # --------------------------------------------------------

    if current_user.workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to a workspace.",
        )

    db: Session = SessionLocal()

    try:

        # ----------------------------------------------------
        # Find document inside user's workspace
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # SPECIAL RULE FOR MEMBERS
        #
        # Members are allowed to remove failed documents.
        # They do NOT get general document deletion access.
        # ----------------------------------------------------

        if current_user.role == "member":

            if document.status != "failed":
                raise HTTPException(
                    status_code=403,
                    detail=(
                        "Members can only delete "
                        "failed documents."
                    ),
                )

        # ----------------------------------------------------
        # NORMAL DELETE PERMISSION
        #
        # Non-members continue to use the existing RBAC /
        # ownership logic.
        # ----------------------------------------------------

        else:

            if not can_delete_document(
                db=db,
                user_id=current_user.id,
                role=current_user.role,
                document_id=document.id,
            ):
                raise HTTPException(
                    status_code=403,
                    detail=(
                        "You do not have permission "
                        "to delete this document."
                    ),
                )

        filename = document.filename
        file_type = document.file_type
        storage_key = document.storage_key

        # ----------------------------------------------------
        # Delete MinIO file
        # ----------------------------------------------------

        try:

            delete_file(
                storage_key
            )

        except Exception as exc:

            raise HTTPException(
                status_code=500,
                detail=(
                    "Failed to delete stored file: "
                    f"{exc}"
                ),
            )

        # ----------------------------------------------------
        # Delete document chunks
        # ----------------------------------------------------

        db.query(
            DocumentChunk
        ).filter(
            DocumentChunk.document_id
            == document.id
        ).delete(
            synchronize_session=False
        )

        # ----------------------------------------------------
        # Delete document permissions
        # ----------------------------------------------------

        db.query(
            DocumentPermission
        ).filter(
            DocumentPermission.document_id
            == document.id
        ).delete(
            synchronize_session=False
        )

        # ----------------------------------------------------
        # Create audit log
        # ----------------------------------------------------

        create_audit_log(
            db,
            workspace_id=current_user.workspace_id,
            user_id=current_user.id,
            action="DOCUMENT_DELETED",
            resource_type="document",
            resource_id=document.id,
            details={
                "filename": filename,
                "file_type": file_type,
                "storage_key": storage_key,
                "status": document.status,
                "deleted_by_role": current_user.role,
            },
        )

        # ----------------------------------------------------
        # Delete document
        # ----------------------------------------------------

        db.delete(document)

        db.commit()

        # ----------------------------------------------------
        # Response
        # ----------------------------------------------------

        return {
            "message": (
                "Document deleted successfully"
            ),
            "document_id": document_id,
        }

    except HTTPException:

        db.rollback()
        raise

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()
