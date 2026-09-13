"""add document chunk timestamp default

Revision ID: 94c7c65c8c6b
Revises: cabd7cfba4d1
Create Date: 2026-08-12 17:44:17.102145

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision: str = "94c7c65c8c6b"
down_revision: Union[str, Sequence[str], None] = "cabd7cfba4d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column(
        "document_chunks",
        "created_at",
        existing_type=sa.DateTime(),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "document_chunks",
        "created_at",
        existing_type=sa.DateTime(),
        server_default=None,
        existing_nullable=False,
    )
