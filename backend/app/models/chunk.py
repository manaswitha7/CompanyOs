from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.database.database import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    document_id = Column(
        Integer,
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )

    chunk_index = Column(
        Integer,
        nullable=False,
    )

    page_number = Column(
        Integer,
        nullable=True,
    )

    content = Column(
        Text,
        nullable=False,
    )

    embedding = Column(
        Vector(384),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
