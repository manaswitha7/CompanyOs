from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.database import get_db

# ============================================================
# STORAGE
# ============================================================

from app.services.storage.minio import (
    create_bucket_if_not_exists,
)


# ============================================================
# API ROUTERS
# ============================================================
from app.api.routes.connectors import (
    router as connectors_router,
)
from app.api.documents import router as documents_router
from app.api.ingestion import router as ingestion_router
from app.api.search import router as search_router

from app.api.routes.auth import router as auth_router
from app.api.routes.chat import router as chat_router
from app.api.routes.chat_sessions import (
    router as chat_sessions_router,
)
from app.api.routes.system import router as system_router
from app.api.routes.tools import router as tools_router
from app.api.routes.evaluation import (
    router as evaluation_router,
)
from app.api.routes.users import router as users_router
from app.api.routes.tasks import router as tasks_router
from app.api.routes.organization import (
    router as organization_router,
)
from app.api.routes.structured_data import (
    router as structured_data_router,
)
from app.api.routes.entity_resolution import (
    router as entity_resolution_router,
)
from app.api.routes.team_views import (
    router as team_views_router,
)
from app.api.routes.cross_team_context import (
    router as cross_team_context_router,
)
from app.api.routes.workflows import router as workflows_router
from app.api.routes.crm import router as crm_router
from app.api.routes.meetings import router as meetings_router
from app.api.routes.platform import router as platform_router
from app.api.lineage import router as lineage_router
from app.api.routes.reports import router as reports_router
from app.api.routes.tools import router as tools_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.notifications import (
    router as notifications_router,
)
from app.api.routes.knowledge_governance import (
    router as knowledge_governance_router,
)
from app.api.routes.agents import router as agents_router
# ============================================================
# MODELS
# ============================================================
# Importing models here ensures SQLAlchemy/Alembic knows about
# all models before the application starts.
# ============================================================

from app.models.user import User
from app.models.workspace import Workspace
from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.models.task import Task
from app.models.department import Department
from app.models.team import Team
from app.models.document_source import DocumentSource
from app.models.company import Company
from app.models.person import Person
from app.models.project import Project
from app.models.audit_log import AuditLog


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Company OS API",
    version="0.1.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTERS
# ============================================================

# Documents
app.include_router(
    documents_router
)

# Ingestion
app.include_router(
    ingestion_router
)

# Search
app.include_router(
    search_router
)

# Chat
app.include_router(
    chat_router
)

# Authentication
app.include_router(
    auth_router
)

# Chat sessions
app.include_router(
    chat_sessions_router
)

# System
app.include_router(
    system_router
)

# Tools / MCP-related endpoints
app.include_router(
    tools_router
)

# Evaluation
app.include_router(
    evaluation_router
)

# Users / RBAC
app.include_router(
    users_router
)

# Document lineage
app.include_router(
    lineage_router
)

# Organization
app.include_router(
    organization_router
)

# Tasks
app.include_router(
    tasks_router
)

# Connectors
app.include_router(
    connectors_router
)

# Meetings
app.include_router(
    meetings_router
)

# Structured data
app.include_router(
    structured_data_router
)
# CRM
app.include_router(
    crm_router
)

# Platform
app.include_router(
    platform_router
)

# Team views
app.include_router(team_views_router)
# Tools
app.include_router(tools_router)

app.include_router(workflows_router)

app.include_router(
    entity_resolution_router
)
app.include_router(reports_router)
app.include_router(cross_team_context_router)
app.include_router(analytics_router)
app.include_router(
    notifications_router
)
app.include_router(
    knowledge_governance_router
)

app.include_router(agents_router)
# ============================================================
# STARTUP
# ============================================================


@app.on_event("startup")
def startup():
    create_bucket_if_not_exists()


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get(
    "/health",
    tags=["Health"],
)
def health_check():
    return {
        "status": "ok",
    }


# ============================================================
# DATABASE HEALTH CHECK
# ============================================================

@app.get(
    "/health/db",
    tags=["Health"],
)
def database_health(
    db: Session = Depends(get_db),
):
    result = db.execute(
        text("SELECT 1")
    )

    return {
        "database": "connected",
        "result": result.scalar(),
    }


# ============================================================
# DEBUG ROUTE SUMMARY
# ============================================================

def _print_registered_routes():
    """
    Print registered routes for development/debugging.

    FastAPI in the current environment may expose included
    routers internally as _IncludedRouter objects, so this
    intentionally handles routes without assuming every object
    has a .path attribute.
    """

    print("\n========== COMPANY OS ROUTES ==========")

    for route in app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)

        if path:
            print(
                f"{sorted(methods) if methods else []} {path}"
            )

    print("=======================================\n")


_print_registered_routes()
