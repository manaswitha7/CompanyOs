"""add company organizational entities

Revision ID: a90fcd859a5b
Revises: 599aa33319b0
Create Date: 2026-08-16

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a90fcd859a5b"
down_revision: Union[str, Sequence[str], None] = "599aa33319b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add company organizational entities.

    Existing departments and teams tables are preserved.
    """

    # ---------------------------------------------------------
    # COMPANIES
    # ---------------------------------------------------------

    op.create_table(
        "companies",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "workspace_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_by",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_companies_workspace_id",
        "companies",
        ["workspace_id"],
        unique=False,
    )

    op.create_index(
        "ix_companies_created_by",
        "companies",
        ["created_by"],
        unique=False,
    )

    # ---------------------------------------------------------
    # PEOPLE
    # ---------------------------------------------------------

    op.create_table(
        "people",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "workspace_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "company_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "role",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
        ),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_people_workspace_id",
        "people",
        ["workspace_id"],
        unique=False,
    )

    op.create_index(
        "ix_people_company_id",
        "people",
        ["company_id"],
        unique=False,
    )

    op.create_index(
        "ix_people_email",
        "people",
        ["email"],
        unique=False,
    )

    # ---------------------------------------------------------
    # PROJECTS
    # ---------------------------------------------------------

    op.create_table(
        "projects",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "workspace_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "company_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "created_by",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
        ),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_projects_workspace_id",
        "projects",
        ["workspace_id"],
        unique=False,
    )

    op.create_index(
        "ix_projects_company_id",
        "projects",
        ["company_id"],
        unique=False,
    )

    op.create_index(
        "ix_projects_created_by",
        "projects",
        ["created_by"],
        unique=False,
    )


def downgrade() -> None:
    """Remove company organizational entities."""

    op.drop_index(
        "ix_projects_created_by",
        table_name="projects",
    )

    op.drop_index(
        "ix_projects_company_id",
        table_name="projects",
    )

    op.drop_index(
        "ix_projects_workspace_id",
        table_name="projects",
    )

    op.drop_table("projects")

    op.drop_index(
        "ix_people_email",
        table_name="people",
    )

    op.drop_index(
        "ix_people_company_id",
        table_name="people",
    )

    op.drop_index(
        "ix_people_workspace_id",
        table_name="people",
    )

    op.drop_table("people")

    op.drop_index(
        "ix_companies_created_by",
        table_name="companies",
    )

    op.drop_index(
        "ix_companies_workspace_id",
        table_name="companies",
    )

    op.drop_table("companies")
