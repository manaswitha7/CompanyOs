"""add chunk embeddings

Revision ID: cabd7cfba4d1
Revises: 5caac17b3aa4
Create Date: 2026-08-12 16:22:42.371748

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.

revision: str = "cabd7cfba4d1"
down_revision: Union[str, Sequence[str], None] = "5caac17b3aa4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "document_chunks",
        sa.Column(
            "embedding",
            Vector(384),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "document_chunks",
        "embedding",
    )
