from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class ExternalIdentity(Base):
    """
    Maps an identity from an external system to a Company OS user.
    """

    __tablename__ = "external_identities"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    workspace_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    connector_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("connectors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    external_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    external_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    external_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
    )

    metadata_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class ExternalResource(Base):
    """
    Represents a resource coming from an external system.

    Examples:
    - Slack channel
    - Google Drive file
    - GitHub repository
    - Jira issue
    - Confluence page
    """

    __tablename__ = "external_resources"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    workspace_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    connector_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("connectors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    external_id: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
    )

    resource_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    name: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
    )

    metadata_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class ExternalPermission(Base):
    """
    Stores permissions synchronized from an external system.

    This allows Company OS to determine whether a user is allowed
    to access an externally sourced resource.
    """

    __tablename__ = "external_permissions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    workspace_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    connector_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("connectors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    external_resource_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "external_resources.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    external_identity_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "external_identities.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    permission: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="read",
        server_default="read",
    )

    granted: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
    )

    source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    metadata_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    synced_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
