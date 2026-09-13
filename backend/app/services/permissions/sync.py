from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.external_permission import ExternalPermission


class PermissionSyncService:
    """
    Synchronizes permissions from external systems
    into Company OS.
    """

    def sync(
        self,
        db: Session,
        connector_id: int,
        records: list[dict[str, Any]],
    ) -> dict[str, Any]:

        created = 0
        updated = 0

        for record in records:

            external_resource_id = str(
                record["external_resource_id"]
            )

            principal = record["principal"]

            existing = (
                db.query(ExternalPermission)
                .filter(
                    ExternalPermission.connector_id
                    == connector_id,
                    ExternalPermission.external_resource_id
                    == external_resource_id,
                    ExternalPermission.principal
                    == principal,
                )
                .first()
            )

            if existing:

                existing.resource_type = record.get(
                    "resource_type",
                    existing.resource_type,
                )

                existing.permission = record.get(
                    "permission",
                    existing.permission,
                )

                existing.principal_type = record.get(
                    "principal_type",
                    existing.principal_type,
                )

                existing.source_uri = record.get(
                    "source_uri",
                    existing.source_uri,
                )

                existing.synced_at = datetime.utcnow()

                updated += 1

            else:

                permission = ExternalPermission(
                    connector_id=connector_id,
                    external_resource_id=external_resource_id,
                    resource_type=record.get(
                        "resource_type",
                        "unknown",
                    ),
                    principal=principal,
                    principal_type=record.get(
                        "principal_type",
                        "user",
                    ),
                    permission=record.get(
                        "permission",
                        "read",
                    ),
                    source_uri=record.get(
                        "source_uri"
                    ),
                )

                db.add(permission)
                created += 1

        db.commit()

        return {
            "connector_id": connector_id,
            "created": created,
            "updated": updated,
            "total": created + updated,
        }

    def check_access(
        self,
        db: Session,
        connector_id: int,
        external_resource_id: str,
        principal: str,
    ) -> bool:

        permission = (
            db.query(ExternalPermission)
            .filter(
                ExternalPermission.connector_id
                == connector_id,
                ExternalPermission.external_resource_id
                == external_resource_id,
                ExternalPermission.principal
                == principal,
            )
            .first()
        )

        if not permission:
            return False

        return permission.permission.lower() in {
            "read",
            "write",
            "edit",
            "admin",
            "owner",
        }

    def get_permissions(
        self,
        db: Session,
        connector_id: int,
        external_resource_id: str,
    ) -> list[ExternalPermission]:

        return (
            db.query(ExternalPermission)
            .filter(
                ExternalPermission.connector_id
                == connector_id,
                ExternalPermission.external_resource_id
                == external_resource_id,
            )
            .all()
        )

    def delete_resource_permissions(
        self,
        db: Session,
        connector_id: int,
        external_resource_id: str,
    ) -> int:

        permissions = (
            db.query(ExternalPermission)
            .filter(
                ExternalPermission.connector_id
                == connector_id,
                ExternalPermission.external_resource_id
                == external_resource_id,
            )
            .all()
        )

        count = len(permissions)

        for permission in permissions:
            db.delete(permission)

        db.commit()

        return count


permission_sync_service = PermissionSyncService()
