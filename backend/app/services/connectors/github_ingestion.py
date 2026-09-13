from typing import Any

from app.database.database import SessionLocal
from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.connectors.github import GitHubConnector
from app.services.ingestion.chunker import chunk_text
from app.services.embeddings.embedder import embedding_service


class GitHubIngestionService:
    """
    Fetch GitHub data and ingest it into the Company OS
    document/chunk/embedding pipeline.

    Pipeline:

        GitHub
          ↓
        Fetch issues / PRs
          ↓
        Normalize records
          ↓
        Create Document
          ↓
        Chunk
          ↓
        Embeddings
          ↓
        PostgreSQL / pgvector
          ↓
        RAG
    """

    def __init__(self):
        self.connector = GitHubConnector()

    # ============================================================
    # CONNECT
    # ============================================================

    def connect(
        self,
        credentials: dict[str, Any],
    ) -> dict[str, Any]:

        return self.connector.connect(
            credentials
        )

    # ============================================================
    # TEST CONNECTION
    # ============================================================

    def test_connection(
        self,
        credentials: dict[str, Any],
    ) -> dict[str, Any]:

        self.connector.connect(credentials)

        return self.connector.test_connection()

    # ============================================================
    # FETCH
    # ============================================================

    def fetch(
        self,
        credentials: dict[str, Any],
        repository: str,
        limit: int = 10,
        state: str = "open",
    ) -> list[dict[str, Any]]:

        self.connector.connect(credentials)

        return self.connector.fetch(
            repository=repository,
            limit=limit,
            state=state,
        )

    # ============================================================
    # INGEST
    # ============================================================

    def ingest(
        self,
        credentials: dict[str, Any],
        repository: str,
        workspace_id: int,
        owner_id: int,
        limit: int = 10,
        state: str = "open",
    ) -> dict[str, Any]:

        db = SessionLocal()

        try:

            # ----------------------------------------------------
            # 1. FETCH FROM GITHUB
            # ----------------------------------------------------

            records = self.fetch(
                credentials=credentials,
                repository=repository,
                limit=limit,
                state=state,
            )

            if not records:

                return {
                    "success": True,
                    "repository": repository,
                    "records_fetched": 0,
                    "documents_created": 0,
                    "chunks_created": 0,
                    "message": (
                        "No GitHub records found."
                    ),
                }

            documents_created = 0
            chunks_created = 0

            # ----------------------------------------------------
            # 2. PROCESS EACH GITHUB RECORD
            # ----------------------------------------------------

            for record in records:

                title = (
                    record.get("title")
                    or record.get("name")
                    or "GitHub Record"
                )

                description = (
                    record.get("description")
                    or record.get("text")
                    or ""
                )

                record_type = (
                    record.get("type")
                    or "github_record"
                )

                external_id = record.get(
                    "id"
                )

                # ------------------------------------------------
                # Build searchable text
                # ------------------------------------------------

                content = f"""
GitHub Repository: {repository}

Type: {record_type}

Title:
{title}

Description:
{description}

State:
{record.get("state", "")}

Author:
{record.get("author", "")}

URL:
{record.get("url", "")}

Labels:
{", ".join(record.get("labels", []))}
""".strip()

                if not content:
                    continue

                # ------------------------------------------------
                # 3. CREATE DOCUMENT
                # ------------------------------------------------

                filename = (
                    f"github_{repository.replace('/', '_')}_"
                    f"{record_type}_{external_id}.txt"
                )

                document = Document(
                    workspace_id=workspace_id,
                    owner_id=owner_id,
                    filename=filename,
                    file_type="github",
                    storage_key=(
                        f"github://{repository}/"
                        f"{record_type}/{external_id}"
                    ),
                    status="processed",
                )

                db.add(document)

                db.flush()

                documents_created += 1

                # ------------------------------------------------
                # 4. CHUNK
                # ------------------------------------------------

                text_chunks = chunk_text(
                    content,
                    chunk_size=1000,
                    chunk_overlap=150,
                )

                if not text_chunks:
                    continue

                # ------------------------------------------------
                # 5. EMBEDDINGS
                # ------------------------------------------------

                embeddings = (
                    embedding_service.embed_texts(
                        text_chunks
                    )
                )

                if not embeddings:
                    continue

                # ------------------------------------------------
                # 6. STORE CHUNKS
                # ------------------------------------------------

                for index, (
                    chunk_content,
                    embedding,
                ) in enumerate(
                    zip(
                        text_chunks,
                        embeddings,
                    )
                ):

                    chunk = DocumentChunk(
                        document_id=document.id,
                        chunk_index=index,
                        page_number=None,
                        content=chunk_content,
                        embedding=embedding,
                    )

                    db.add(chunk)

                    chunks_created += 1

            # ----------------------------------------------------
            # 7. COMMIT
            # ----------------------------------------------------

            db.commit()

            return {
                "success": True,
                "repository": repository,
                "records_fetched": len(records),
                "documents_created": documents_created,
                "chunks_created": chunks_created,
                "message": (
                    "GitHub data ingested successfully."
                ),
            }

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()


# ================================================================
# SINGLETON SERVICE
# ================================================================

github_ingestion_service = (
    GitHubIngestionService()
)
