import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.connector import Connector

from app.models.platform import (
    ConnectorPermission,
    Entity,
    EntityAlias,
    KnowledgeEdge,
    KnowledgeVersion,
    AIInsight,
    AIFeedback,
    AgentDefinition,
    WorkspaceView,
    PlatformFeature,
)

# Workflow has its own dedicated model.
from app.models.workflow import Workflow


class PlatformService:

    # ========================================================
    # CONNECTORS
    # ========================================================

    @staticmethod
    def create_connector(
        db: Session,
        workspace_id: int,
        name: str,
        connector_type: str,
        config: dict | None = None,
    ):
        connector = Connector(
            workspace_id=workspace_id,
            name=name,
            connector_type=connector_type,
            status="inactive",
            config=config or {},
        )

        db.add(connector)
        db.commit()
        db.refresh(connector)

        return connector

    @staticmethod
    def list_connectors(
        db: Session,
        workspace_id: int,
    ):
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

    @staticmethod
    def update_connector_status(
        db: Session,
        connector_id: int,
        status: str,
    ):
        connector = (
            db.query(Connector)
            .filter(
                Connector.id == connector_id
            )
            .first()
        )

        if not connector:
            return None

        connector.status = status

        if status == "connected":
            connector.last_sync_at = datetime.utcnow()
            connector.last_sync_status = "success"
            connector.last_sync_error = None

        elif status in {
            "error",
            "failed",
        }:
            connector.last_sync_status = "failed"

        db.commit()
        db.refresh(connector)

        return connector

    # ========================================================
    # WORKFLOWS
    # ========================================================

    @staticmethod
    def create_workflow(
        db: Session,
        workspace_id: int,
        name: str,
        trigger_type: str,
        condition: dict | None,
        action: dict | None,
        description: str | None = None,
    ):
        workflow = Workflow(
            workspace_id=workspace_id,
            name=name,
            description=description,
            trigger_type=trigger_type,
            condition_json=json.dumps(
                condition or {}
            ),
            action_json=json.dumps(
                action or {}
            ),
            enabled=True,
        )

        db.add(workflow)
        db.commit()
        db.refresh(workflow)

        return workflow

    @staticmethod
    def list_workflows(
        db: Session,
        workspace_id: int,
    ):
        return (
            db.query(Workflow)
            .filter(
                Workflow.workspace_id == workspace_id
            )
            .order_by(
                Workflow.created_at.desc()
            )
            .all()
        )

    # ========================================================
    # ENTITY RESOLUTION
    # ========================================================

    @staticmethod
    def create_entity(
        db: Session,
        workspace_id: int,
        entity_type: str,
        canonical_name: str,
        canonical_email: str | None = None,
        metadata: dict | None = None,
    ):
        entity = Entity(
            workspace_id=workspace_id,
            entity_type=entity_type,
            canonical_name=canonical_name,
            canonical_email=canonical_email,
            metadata_json=json.dumps(
                metadata or {}
            ),
        )

        db.add(entity)
        db.commit()
        db.refresh(entity)

        return entity

    @staticmethod
    def add_alias(
        db: Session,
        entity_id: int,
        alias: str,
        source: str | None = None,
        confidence: float = 1.0,
    ):
        entity_alias = EntityAlias(
            entity_id=entity_id,
            alias=alias,
            source=source,
            confidence=confidence,
        )

        db.add(entity_alias)
        db.commit()
        db.refresh(entity_alias)

        return entity_alias

    @staticmethod
    def resolve_entity(
        db: Session,
        workspace_id: int,
        value: str,
    ):
        entity = (
            db.query(Entity)
            .filter(
                Entity.workspace_id == workspace_id,
                Entity.canonical_name.ilike(value),
            )
            .first()
        )

        if entity:
            return entity

        alias = (
            db.query(EntityAlias)
            .join(Entity)
            .filter(
                Entity.workspace_id == workspace_id,
                EntityAlias.alias.ilike(value),
            )
            .order_by(
                EntityAlias.confidence.desc()
            )
            .first()
        )

        if alias:
            return (
                db.query(Entity)
                .filter(
                    Entity.id == alias.entity_id
                )
                .first()
            )

        return None

    # ========================================================
    # KNOWLEDGE GRAPH
    # ========================================================

    @staticmethod
    def create_edge(
        db: Session,
        workspace_id: int,
        source_entity_id: int,
        target_entity_id: int,
        relationship_type: str,
        confidence: float = 1.0,
        metadata: dict | None = None,
    ):
        edge = KnowledgeEdge(
            workspace_id=workspace_id,
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            relationship_type=relationship_type,
            confidence=confidence,
            metadata_json=json.dumps(
                metadata or {}
            ),
        )

        db.add(edge)
        db.commit()
        db.refresh(edge)

        return edge

    @staticmethod
    def get_graph(
        db: Session,
        workspace_id: int,
    ):
        return (
            db.query(KnowledgeEdge)
            .filter(
                KnowledgeEdge.workspace_id
                == workspace_id
            )
            .all()
        )

    # ========================================================
    # AI INSIGHTS
    # ========================================================

    @staticmethod
    def create_insight(
        db: Session,
        workspace_id: int,
        insight_type: str,
        title: str,
        content: str,
        priority: str = "normal",
        source_type: str | None = None,
        source_id: int | None = None,
    ):
        insight = AIInsight(
            workspace_id=workspace_id,
            insight_type=insight_type,
            title=title,
            content=content,
            priority=priority,
            source_type=source_type,
            source_id=source_id,
        )

        db.add(insight)
        db.commit()
        db.refresh(insight)

        return insight

    @staticmethod
    def list_insights(
        db: Session,
        workspace_id: int,
    ):
        return (
            db.query(AIInsight)
            .filter(
                AIInsight.workspace_id
                == workspace_id
            )
            .order_by(
                AIInsight.created_at.desc()
            )
            .all()
        )

    # ========================================================
    # AGENTS
    # ========================================================

    @staticmethod
    def create_agent(
        db: Session,
        workspace_id: int,
        name: str,
        description: str | None = None,
        system_prompt: str | None = None,
        tools: list | None = None,
        model: str | None = None,
    ):
        agent = AgentDefinition(
            workspace_id=workspace_id,
            name=name,
            description=description,
            system_prompt=system_prompt,
            tools_json=json.dumps(
                tools or []
            ),
            model=model,
            enabled=True,
        )

        db.add(agent)
        db.commit()
        db.refresh(agent)

        return agent

    @staticmethod
    def list_agents(
        db: Session,
        workspace_id: int,
    ):
        return (
            db.query(AgentDefinition)
            .filter(
                AgentDefinition.workspace_id
                == workspace_id
            )
            .order_by(
                AgentDefinition.created_at.desc()
            )
            .all()
        )

    # ========================================================
    # VIEWS
    # ========================================================

    @staticmethod
    def create_view(
        db: Session,
        workspace_id: int,
        name: str,
        view_type: str,
        configuration: dict | None = None,
        created_by: int | None = None,
    ):
        view = WorkspaceView(
            workspace_id=workspace_id,
            name=name,
            view_type=view_type,
            configuration_json=json.dumps(
                configuration or {}
            ),
            created_by=created_by,
        )

        db.add(view)
        db.commit()
        db.refresh(view)

        return view

    @staticmethod
    def list_views(
        db: Session,
        workspace_id: int,
    ):
        return (
            db.query(WorkspaceView)
            .filter(
                WorkspaceView.workspace_id
                == workspace_id
            )
            .order_by(
                WorkspaceView.created_at.desc()
            )
            .all()
        )

    # ========================================================
    # FEEDBACK
    # ========================================================

    @staticmethod
    def create_feedback(
        db: Session,
        workspace_id: int,
        source_type: str,
        rating: int,
        feedback: str | None = None,
        user_id: int | None = None,
        source_id: int | None = None,
    ):
        item = AIFeedback(
            workspace_id=workspace_id,
            user_id=user_id,
            source_type=source_type,
            source_id=source_id,
            rating=rating,
            feedback=feedback,
        )

        db.add(item)
        db.commit()
        db.refresh(item)

        return item

    @staticmethod
    def feedback_stats(
        db: Session,
        workspace_id: int,
    ):
        rows = (
            db.query(AIFeedback)
            .filter(
                AIFeedback.workspace_id
                == workspace_id
            )
            .all()
        )

        if not rows:
            return {
                "total": 0,
                "average_rating": 0,
                "positive": 0,
                "negative": 0,
            }

        ratings = [
            row.rating
            for row in rows
        ]

        return {
            "total": len(rows),
            "average_rating": round(
                sum(ratings) / len(ratings),
                2,
            ),
            "positive": sum(
                1
                for rating in ratings
                if rating >= 4
            ),
            "negative": sum(
                1
                for rating in ratings
                if rating <= 2
            ),
        }


platform_service = PlatformService()
