from sqlalchemy.orm import Session

from app.models.platform import KnowledgeVersion


class KnowledgeGovernanceService:

    @staticmethod
    def create_version(
        db: Session,
        workspace_id: int,
        resource_type: str,
        resource_id: int,
        content: str,
        changed_by: int | None = None,
        change_reason: str | None = None,
    ) -> KnowledgeVersion:

        latest = (
            db.query(KnowledgeVersion)
            .filter(
                KnowledgeVersion.workspace_id == workspace_id,
                KnowledgeVersion.resource_type == resource_type,
                KnowledgeVersion.resource_id == resource_id,
            )
            .order_by(
                KnowledgeVersion.version_number.desc()
            )
            .first()
        )

        next_version = (
            latest.version_number + 1
            if latest
            else 1
        )

        version = KnowledgeVersion(
            workspace_id=workspace_id,
            resource_type=resource_type,
            resource_id=resource_id,
            version_number=next_version,
            content=content,
            changed_by=changed_by,
            change_reason=change_reason,
        )

        db.add(version)
        db.commit()
        db.refresh(version)

        return version

    @staticmethod
    def get_version_history(
        db: Session,
        workspace_id: int,
        resource_type: str,
        resource_id: int,
    ) -> list[KnowledgeVersion]:

        return (
            db.query(KnowledgeVersion)
            .filter(
                KnowledgeVersion.workspace_id == workspace_id,
                KnowledgeVersion.resource_type == resource_type,
                KnowledgeVersion.resource_id == resource_id,
            )
            .order_by(
                KnowledgeVersion.version_number.desc()
            )
            .all()
        )

    @staticmethod
    def get_version(
        db: Session,
        workspace_id: int,
        resource_type: str,
        resource_id: int,
        version_number: int,
    ) -> KnowledgeVersion | None:

        return (
            db.query(KnowledgeVersion)
            .filter(
                KnowledgeVersion.workspace_id == workspace_id,
                KnowledgeVersion.resource_type == resource_type,
                KnowledgeVersion.resource_id == resource_id,
                KnowledgeVersion.version_number == version_number,
            )
            .first()
        )
