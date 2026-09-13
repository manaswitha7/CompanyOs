from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

# Import package so connector registration happens.
import app.connectors

from app.connectors.registry import connector_registry
from app.models.connector import Connector


class ConnectorService:
    """
    Application-level service for external connectors.

    This service sits between:
        API
            ↓
        Connector Registry
            ↓
        External Connector implementation

    It also persists connector state in the Company OS database.
    """

    # ============================================================
    # REGISTRY
    # ============================================================

    def list_registered_connectors(self) -> list[dict[str, Any]]:
        """
        List connector implementations registered in the application.
        """

        return [
            {
                "name": connector.name,
                "display_name": connector.display_name,
            }
            for connector in connector_registry.list()
        ]

    def get_connector(self, name: str):
        """
        Return the registered connector class.
        """

        connector_class = connector_registry.get(name)

        if connector_class is None:
            raise ValueError(
                f"Connector not found: {name}"
            )

        return connector_class

    def create_connector(self, name: str):
        """
        Create an instance of a registered connector.
        """

        connector_class = self.get_connector(name)

        return connector_class()

    # ============================================================
    # DATABASE CONNECTORS
    # ============================================================

    def create_database_connector(
        self,
        db: Session,
        workspace_id: int,
        name: str,
        connector_type: str,
        config: dict[str, Any] | None = None,
        credential_ref: str | None = None,
    ) -> Connector:
        """
        Create a persistent connector record for a workspace.

        Secrets must NOT be stored directly in config.
        """

        # Make sure the connector implementation exists.
        self.get_connector(connector_type)

        connector = Connector(
            workspace_id=workspace_id,
            name=name,
            connector_type=connector_type,
            status="inactive",
            config=config or {},
            credential_ref=credential_ref,
        )

        db.add(connector)
        db.commit()
        db.refresh(connector)

        return connector

    def list_database_connectors(
        self,
        db: Session,
        workspace_id: int,
    ) -> list[Connector]:
        """
        Return all persisted connectors belonging to a workspace.
        """

        return (
            db.query(Connector)
            .filter(
                Connector.workspace_id == workspace_id
            )
            .order_by(
                Connector.created_at.desc()
            )
            .all()
        )

    def get_database_connector(
        self,
        db: Session,
        connector_id: int,
        workspace_id: int | None = None,
    ) -> Connector | None:
        """
        Retrieve a persisted connector.

        If workspace_id is supplied, the connector must belong
        to that workspace.
        """

        query = (
            db.query(Connector)
            .filter(
                Connector.id == connector_id
            )
        )

        if workspace_id is not None:
            query = query.filter(
                Connector.workspace_id == workspace_id
            )

        return query.first()

    # ============================================================
    # CONNECT
    # ============================================================

    def connect(
        self,
        name: str,
        credentials: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Connect directly to an external system.

        This method is useful for testing or stateless operations.
        """

        connector = self.create_connector(name)

        return connector.connect(credentials)

    def connect_database_connector(
        self,
        db: Session,
        connector_id: int,
        credentials: dict[str, Any],
        workspace_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Connect a persisted Company OS connector.

        The credentials are passed to the external connector
        implementation but are NOT persisted as raw secrets.
        """

        db_connector = self.get_database_connector(
            db=db,
            connector_id=connector_id,
            workspace_id=workspace_id,
        )

        if db_connector is None:
            raise ValueError(
                f"Connector not found: {connector_id}"
            )

        connector = self.create_connector(
            db_connector.connector_type
        )

        try:
            result = connector.connect(credentials)

            db_connector.status = "connected"
            db_connector.last_sync_status = "success"
            db_connector.last_sync_error = None
            db_connector.last_sync_at = datetime.utcnow()

            db.commit()
            db.refresh(db_connector)

            return {
                "connector_id": db_connector.id,
                "connector": db_connector.name,
                "status": db_connector.status,
                "result": result,
            }

        except Exception as exc:

            db_connector.status = "error"
            db_connector.last_sync_status = "failed"
            db_connector.last_sync_error = str(exc)

            db.commit()

            raise

    # ============================================================
    # TEST CONNECTION
    # ============================================================

    def test_connection(
        self,
        name: str,
        credentials: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Test a connector without requiring a database record.
        """

        connector = self.create_connector(name)

        if credentials:
            connector.connect(credentials)

        return connector.test_connection()

    def test_database_connector(
        self,
        db: Session,
        connector_id: int,
        credentials: dict[str, Any] | None = None,
        workspace_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Test a persisted connector.
        """

        db_connector = self.get_database_connector(
            db=db,
            connector_id=connector_id,
            workspace_id=workspace_id,
        )

        if db_connector is None:
            raise ValueError(
                f"Connector not found: {connector_id}"
            )

        connector = self.create_connector(
            db_connector.connector_type
        )

        try:

            if credentials:
                connector.connect(credentials)

            result = connector.test_connection()

            db_connector.last_sync_status = "success"
            db_connector.last_sync_error = None

            db.commit()
            db.refresh(db_connector)

            return {
                "connector_id": db_connector.id,
                "connector": db_connector.name,
                "status": "healthy",
                "result": result,
            }

        except Exception as exc:

            db_connector.last_sync_status = "failed"
            db_connector.last_sync_error = str(exc)

            db.commit()

            raise

    # ============================================================
    # DISCONNECT
    # ============================================================

    def disconnect(
        self,
        name: str,
    ) -> dict[str, Any]:
        """
        Disconnect a connector instance.
        """

        connector = self.create_connector(name)

        return connector.disconnect()

    def disconnect_database_connector(
        self,
        db: Session,
        connector_id: int,
        workspace_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Disconnect a persisted connector and update its state.
        """

        db_connector = self.get_database_connector(
            db=db,
            connector_id=connector_id,
            workspace_id=workspace_id,
        )

        if db_connector is None:
            raise ValueError(
                f"Connector not found: {connector_id}"
            )

        connector = self.create_connector(
            db_connector.connector_type
        )

        try:

            result = connector.disconnect()

            db_connector.status = "inactive"
            db_connector.last_sync_status = "success"
            db_connector.last_sync_error = None

            db.commit()
            db.refresh(db_connector)

            return {
                "connector_id": db_connector.id,
                "connector": db_connector.name,
                "status": db_connector.status,
                "result": result,
            }

        except Exception as exc:

            db_connector.last_sync_status = "failed"
            db_connector.last_sync_error = str(exc)

            db.commit()

            raise

    # ============================================================
    # FETCH
    # ============================================================

    def fetch(
        self,
        name: str,
        credentials: dict[str, Any],
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Fetch data directly from an external connector.
        """

        connector = self.create_connector(name)

        connector.connect(credentials)

        return connector.fetch(**kwargs)

    def fetch_database_connector(
        self,
        db: Session,
        connector_id: int,
        credentials: dict[str, Any],
        workspace_id: int | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Fetch data using a persisted connector.
        """

        db_connector = self.get_database_connector(
            db=db,
            connector_id=connector_id,
            workspace_id=workspace_id,
        )

        if db_connector is None:
            raise ValueError(
                f"Connector not found: {connector_id}"
            )

        connector = self.create_connector(
            db_connector.connector_type
        )

        try:

            connector.connect(credentials)

            records = connector.fetch(**kwargs)

            db_connector.status = "connected"
            db_connector.last_sync_status = "success"
            db_connector.last_sync_error = None
            db_connector.last_sync_at = datetime.utcnow()

            db.commit()

            return records

        except Exception as exc:

            db_connector.last_sync_status = "failed"
            db_connector.last_sync_error = str(exc)

            db.commit()

            raise

    # ============================================================
    # NORMALIZE
    # ============================================================

    def normalize(
        self,
        name: str,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Normalize external records into Company OS format.
        """

        connector = self.create_connector(name)

        return connector.normalize(records)


connector_service = ConnectorService()
