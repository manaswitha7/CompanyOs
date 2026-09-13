import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.database.database import SessionLocal
from app.models.platform import (
    ConnectorPermission,
    Entity,
    AgentDefinition,
    WorkspaceView,
    AIInsight,
)
from app.services.platform import platform_service


router = APIRouter(
    prefix="/platform",
    tags=["Platform"],
)


# ============================================================
# REQUEST MODELS
# ============================================================


class ConnectorCreate(BaseModel):
    workspace_id: int
    name: str
    connector_type: str
    config: dict = {}


class ConnectorStatusUpdate(BaseModel):
    status: str


class WorkflowCreate(BaseModel):
    workspace_id: int
    name: str
    trigger_type: str
    condition: dict = {}
    action: dict = {}
    description: str | None = None


class EntityCreate(BaseModel):
    workspace_id: int
    entity_type: str
    canonical_name: str
    canonical_email: str | None = None
    metadata: dict = {}


class AliasCreate(BaseModel):
    alias: str
    source: str | None = None
    confidence: float = Field(
        default=1.0,
        ge=0,
        le=1,
    )


class EdgeCreate(BaseModel):
    workspace_id: int
    source_entity_id: int
    target_entity_id: int
    relationship_type: str
    confidence: float = Field(
        default=1.0,
        ge=0,
        le=1,
    )
    metadata: dict = {}


class AgentCreate(BaseModel):
    workspace_id: int
    name: str
    description: str | None = None
    system_prompt: str | None = None
    tools: list = []
    model: str | None = None


class ViewCreate(BaseModel):
    workspace_id: int
    name: str
    view_type: str
    configuration: dict = {}
    created_by: int | None = None


class InsightCreate(BaseModel):
    workspace_id: int
    insight_type: str
    title: str
    content: str
    priority: str = "normal"
    source_type: str | None = None
    source_id: int | None = None


class FeedbackCreate(BaseModel):
    workspace_id: int
    source_type: str
    source_id: int | None = None
    rating: int = Field(
        ge=1,
        le=5,
    )
    feedback: str | None = None
    user_id: int | None = None


# ============================================================
# FEATURE STATUS
# ============================================================


@router.get("/feature-status")
def feature_status():

    return {
        "features": [
            {
                "number": 23,
                "name": "Advanced Data Integration",
                "status": "implemented",
            },
            {
                "number": 24,
                "name": "Connector Framework",
                "status": "implemented",
            },
            {
                "number": 25,
                "name": "External Connectors",
                "status": "framework",
            },
            {
                "number": 26,
                "name": "Permission Synchronization",
                "status": "implemented",
            },
            {
                "number": 27,
                "name": "Voice & Meeting Intelligence",
                "status": "implemented",
            },
            {
                "number": 28,
                "name": "Structured Data Intelligence",
                "status": "implemented",
            },
            {
                "number": 29,
                "name": "Super CRM",
                "status": "implemented",
            },
            {
                "number": 30,
                "name": "Team Workspaces & Views",
                "status": "implemented",
            },
            {
                "number": 31,
                "name": "Workflow Automation",
                "status": "implemented",
            },
            {
                "number": 32,
                "name": "Advanced MCP & Tooling",
                "status": "foundation",
            },
            {
                "number": 33,
                "name": "Agent Orchestration",
                "status": "implemented",
            },
            {
                "number": 34,
                "name": "Entity Resolution",
                "status": "implemented",
            },
            {
                "number": 35,
                "name": "Knowledge / Company Graph",
                "status": "implemented",
            },
            {
                "number": 36,
                "name": "Cross-Team Context",
                "status": "implemented",
            },
            {
                "number": 37,
                "name": "AI Productivity Features",
                "status": "implemented",
            },
            {
                "number": 38,
                "name": "Knowledge Governance",
                "status": "implemented",
            },
            {
                "number": 39,
                "name": "Feedback & Usage Analytics",
                "status": "implemented",
            },
        ]
    }


# ============================================================
# CONNECTORS
# ============================================================


@router.post("/connectors")
def create_connector(request: ConnectorCreate):

    db = SessionLocal()

    try:
        connector = platform_service.create_connector(
            db=db,
            workspace_id=request.workspace_id,
            name=request.name,
            connector_type=request.connector_type,
            config=request.config,
        )

        return {
            "id": connector.id,
            "workspace_id": connector.workspace_id,
            "name": connector.name,
            "connector_type": connector.connector_type,
            "status": connector.status,
        }

    finally:
        db.close()


@router.get("/connectors/{workspace_id}")
def get_connectors(workspace_id: int):

    db = SessionLocal()

    try:
        connectors = platform_service.list_connectors(
            db,
            workspace_id,
        )

        return [
            {
                "id": item.id,
                "name": item.name,
                "type": item.connector_type,
                "status": item.status,
                "last_sync_at": item.last_sync_at,
            }
            for item in connectors
        ]

    finally:
        db.close()


@router.patch("/connectors/{connector_id}/status")
def update_connector_status(
    connector_id: int,
    request: ConnectorStatusUpdate,
):

    db = SessionLocal()

    try:
        connector = platform_service.update_connector_status(
            db,
            connector_id,
            request.status,
        )

        if not connector:
            raise HTTPException(
                status_code=404,
                detail="Connector not found",
            )

        return {
            "id": connector.id,
            "status": connector.status,
            "last_sync_at": connector.last_sync_at,
        }

    finally:
        db.close()


# ============================================================
# WORKFLOWS
# ============================================================


@router.post("/workflows")
def create_workflow(request: WorkflowCreate):

    db = SessionLocal()

    try:
        workflow = platform_service.create_workflow(
            db=db,
            workspace_id=request.workspace_id,
            name=request.name,
            trigger_type=request.trigger_type,
            condition=request.condition,
            action=request.action,
            description=request.description,
        )

        return {
            "id": workflow.id,
            "name": workflow.name,
            "trigger_type": workflow.trigger_type,
            "enabled": workflow.enabled,
        }

    finally:
        db.close()


@router.get("/workflows/{workspace_id}")
def get_workflows(workspace_id: int):

    db = SessionLocal()

    try:
        workflows = platform_service.list_workflows(
            db,
            workspace_id,
        )

        return [
            {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "trigger_type": item.trigger_type,
                "condition": json.loads(
                    item.condition_json or "{}"
                ),
                "action": json.loads(
                    item.action_json or "{}"
                ),
                "enabled": item.enabled,
            }
            for item in workflows
        ]

    finally:
        db.close()


# ============================================================
# ENTITY RESOLUTION
# ============================================================


@router.post("/entities")
def create_entity(request: EntityCreate):

    db = SessionLocal()

    try:
        entity = platform_service.create_entity(
            db=db,
            workspace_id=request.workspace_id,
            entity_type=request.entity_type,
            canonical_name=request.canonical_name,
            canonical_email=request.canonical_email,
            metadata=request.metadata,
        )

        return {
            "id": entity.id,
            "type": entity.entity_type,
            "name": entity.canonical_name,
            "email": entity.canonical_email,
        }

    finally:
        db.close()


@router.get("/entities/{workspace_id}")
def get_entities(workspace_id: int):

    db = SessionLocal()

    try:
        entities = (
            db.query(Entity)
            .filter(
                Entity.workspace_id == workspace_id
            )
            .order_by(Entity.created_at.desc())
            .all()
        )

        return [
            {
                "id": entity.id,
                "type": entity.entity_type,
                "name": entity.canonical_name,
                "email": entity.canonical_email,
                "metadata": json.loads(
                    entity.metadata_json or "{}"
                ),
            }
            for entity in entities
        ]

    finally:
        db.close()


@router.post("/entities/{entity_id}/aliases")
def create_alias(
    entity_id: int,
    request: AliasCreate,
):

    db = SessionLocal()

    try:
        entity = (
            db.query(Entity)
            .filter(Entity.id == entity_id)
            .first()
        )

        if not entity:
            raise HTTPException(
                status_code=404,
                detail="Entity not found",
            )

        alias = platform_service.add_alias(
            db=db,
            entity_id=entity_id,
            alias=request.alias,
            source=request.source,
            confidence=request.confidence,
        )

        return {
            "id": alias.id,
            "entity_id": alias.entity_id,
            "alias": alias.alias,
            "confidence": alias.confidence,
        }

    finally:
        db.close()


# ============================================================
# KNOWLEDGE GRAPH
# ============================================================


@router.post("/graph/edges")
def create_edge(request: EdgeCreate):

    db = SessionLocal()

    try:
        edge = platform_service.create_edge(
            db=db,
            workspace_id=request.workspace_id,
            source_entity_id=request.source_entity_id,
            target_entity_id=request.target_entity_id,
            relationship_type=request.relationship_type,
            confidence=request.confidence,
            metadata=request.metadata,
        )

        return {
            "id": edge.id,
            "source": edge.source_entity_id,
            "target": edge.target_entity_id,
            "relationship": edge.relationship_type,
            "confidence": edge.confidence,
        }

    finally:
        db.close()


@router.get("/graph/{workspace_id}")
def get_graph(workspace_id: int):

    db = SessionLocal()

    try:
        edges = platform_service.get_graph(
            db,
            workspace_id,
        )

        return [
            {
                "id": edge.id,
                "source": edge.source_entity_id,
                "target": edge.target_entity_id,
                "relationship": edge.relationship_type,
                "confidence": edge.confidence,
            }
            for edge in edges
        ]

    finally:
        db.close()


# ============================================================
# AI INSIGHTS
# ============================================================


@router.post("/insights")
def create_insight(request: InsightCreate):

    db = SessionLocal()

    try:
        insight = platform_service.create_insight(
            db=db,
            workspace_id=request.workspace_id,
            insight_type=request.insight_type,
            title=request.title,
            content=request.content,
            priority=request.priority,
            source_type=request.source_type,
            source_id=request.source_id,
        )

        return {
            "id": insight.id,
            "title": insight.title,
            "type": insight.insight_type,
            "priority": insight.priority,
        }

    finally:
        db.close()


@router.get("/insights/{workspace_id}")
def get_insights(workspace_id: int):

    db = SessionLocal()

    try:
        insights = platform_service.list_insights(
            db,
            workspace_id,
        )

        return [
            {
                "id": item.id,
                "type": item.insight_type,
                "title": item.title,
                "content": item.content,
                "priority": item.priority,
                "is_read": item.is_read,
            }
            for item in insights
        ]

    finally:
        db.close()


# ============================================================
# AGENTS
# ============================================================


@router.post("/agents")
def create_agent(request: AgentCreate):

    db = SessionLocal()

    try:
        agent = platform_service.create_agent(
            db=db,
            workspace_id=request.workspace_id,
            name=request.name,
            description=request.description,
            system_prompt=request.system_prompt,
            tools=request.tools,
            model=request.model,
        )

        return {
            "id": agent.id,
            "name": agent.name,
            "model": agent.model,
            "enabled": agent.enabled,
        }

    finally:
        db.close()


@router.get("/agents/{workspace_id}")
def get_agents(workspace_id: int):

    db = SessionLocal()

    try:
        agents = platform_service.list_agents(
            db,
            workspace_id,
        )

        return [
            {
                "id": agent.id,
                "name": agent.name,
                "description": agent.description,
                "model": agent.model,
                "tools": json.loads(
                    agent.tools_json or "[]"
                ),
                "enabled": agent.enabled,
            }
            for agent in agents
        ]

    finally:
        db.close()


# ============================================================
# WORKSPACE VIEWS
# ============================================================


@router.post("/views")
def create_view(request: ViewCreate):

    db = SessionLocal()

    try:
        view = platform_service.create_view(
            db=db,
            workspace_id=request.workspace_id,
            name=request.name,
            view_type=request.view_type,
            configuration=request.configuration,
            created_by=request.created_by,
        )

        return {
            "id": view.id,
            "name": view.name,
            "view_type": view.view_type,
        }

    finally:
        db.close()


@router.get("/views/{workspace_id}")
def get_views(workspace_id: int):

    db = SessionLocal()

    try:
        views = platform_service.list_views(
            db,
            workspace_id,
        )

        return [
            {
                "id": view.id,
                "name": view.name,
                "view_type": view.view_type,
                "configuration": json.loads(
                    view.configuration_json or "{}"
                ),
            }
            for view in views
        ]

    finally:
        db.close()


# ============================================================
# FEEDBACK
# ============================================================


@router.post("/feedback")
def create_feedback(request: FeedbackCreate):

    db = SessionLocal()

    try:
        feedback = platform_service.create_feedback(
            db=db,
            workspace_id=request.workspace_id,
            source_type=request.source_type,
            source_id=request.source_id,
            rating=request.rating,
            feedback=request.feedback,
            user_id=request.user_id,
        )

        return {
            "id": feedback.id,
            "rating": feedback.rating,
        }

    finally:
        db.close()


@router.get("/feedback/stats/{workspace_id}")
def get_feedback_stats(workspace_id: int):

    db = SessionLocal()

    try:
        return platform_service.feedback_stats(
            db,
            workspace_id,
        )

    finally:
        db.close()
