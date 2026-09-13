from app.database.database import SessionLocal

from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.models.document_source import DocumentSource

from app.services.storage.minio import download_file

from app.services.ingestion.extractor import (
    extract_pdf_pages,
    extract_text,
)

from app.services.ingestion.chunker import (
    chunk_pages,
    chunk_text,
)

from app.services.embeddings.embedder import (
    embedding_service,
)


def process_document(
    document_id: int,
) -> dict:
    """
    Process a document from MinIO into searchable chunks.

    Pipeline:

        MinIO
          ↓
        Extraction
          ↓
        Chunking
          ↓
        Embeddings
          ↓
        PostgreSQL

    Supported formats:

        PDF
        TXT
        MD
        YAML
        YML
        CSV
        JSON
        DOCX
        XLSX
        XLS

    Also records document lineage:

        Original file
              ↓
        DocumentSource
              ↓
        Document
              ↓
        DocumentChunks
    """

    db = SessionLocal()

    try:

        # ====================================================
        # 1. FIND DOCUMENT
        # ====================================================

        document = (
            db.query(Document)
            .filter(
                Document.id == document_id
            )
            .first()
        )

        if not document:

            raise ValueError(
                f"Document {document_id} not found"
            )

        # ====================================================
        # 2. CREATE DOCUMENT SOURCE / LINEAGE
        # ====================================================

        source = (
            db.query(DocumentSource)
            .filter(
                DocumentSource.document_id
                == document.id
            )
            .first()
        )

        if not source:

            source = DocumentSource(
                document_id=document.id,
                source_type="upload",
                source_name=document.filename,
                source_uri=document.storage_key,
                ingestion_method="minio",
            )

            db.add(source)

            db.flush()

        # ====================================================
        # 3. DOWNLOAD FROM MINIO
        # ====================================================

        response = download_file(
            document.storage_key
        )

        if not response:

            raise ValueError(
                "Unable to download document from storage"
            )

        file_body = response.get(
            "Body"
        )

        if file_body is None:

            raise ValueError(
                "Downloaded document has no file body"
            )

        file_bytes = file_body.read()

        if not file_bytes:

            raise ValueError(
                "Downloaded document is empty"
            )

        # ====================================================
        # 4. EXTRACT TEXT
        # ====================================================

        file_type = (
            document.file_type
            .lower()
            .strip()
            .lstrip(".")
        )

        # ----------------------------------------------------
        # PDF
        # ----------------------------------------------------

        if file_type == "pdf":

            pages = extract_pdf_pages(
                file_bytes
            )

            if not pages:

                raise ValueError(
                    "No readable text found in PDF"
                )

            chunks = chunk_pages(
                pages,
                chunk_size=1000,
                chunk_overlap=150,
            )

        # ----------------------------------------------------
        # ALL OTHER SUPPORTED FORMATS
        # ----------------------------------------------------

        else:

            text = extract_text(
                file_bytes,
                file_type,
            )

            if not text or not text.strip():

                raise ValueError(
                    "No readable text found in document"
                )

            text_chunks = chunk_text(
                text,
                chunk_size=1000,
                chunk_overlap=150,
            )

            chunks = [
                {
                    "chunk_index": index,
                    "page_number": None,
                    "content": content,
                }
                for index, content
                in enumerate(text_chunks)
                if content
                and content.strip()
            ]

        # ====================================================
        # 5. VALIDATE CHUNKS
        # ====================================================

        if not chunks:

            raise ValueError(
                "No text chunks were generated"
            )

        # ====================================================
        # 6. GENERATE EMBEDDINGS
        # ====================================================

        texts = [
            chunk["content"]
            for chunk in chunks
        ]

        embeddings = (
            embedding_service.embed_texts(
                texts
            )
        )

        if not embeddings:

            raise ValueError(
                "No embeddings were generated"
            )

        if len(embeddings) != len(chunks):

            raise RuntimeError(
                "Number of embeddings does not "
                "match number of chunks"
            )

        # ====================================================
        # 7. DELETE OLD CHUNKS
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
        # 8. STORE NEW CHUNKS
        # ====================================================

        for chunk_data, embedding in zip(
            chunks,
            embeddings,
        ):

            chunk = DocumentChunk(
                document_id=document.id,

                chunk_index=(
                    chunk_data[
                        "chunk_index"
                    ]
                ),

                page_number=(
                    chunk_data[
                        "page_number"
                    ]
                ),

                content=(
                    chunk_data[
                        "content"
                    ]
                ),

                embedding=embedding,
            )

            db.add(chunk)

        # ====================================================
        # 9. COMMIT
        # ====================================================

        db.commit()

        # ====================================================
        # 10. RETURN RESULT
        # ====================================================

        return {
            "message": (
                "Document processed successfully"
            ),
            "document_id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "total_chunks": len(chunks),
            "embedding_dimension": len(
                embeddings[0]
            ),
            "source_id": source.id,
        }

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()
