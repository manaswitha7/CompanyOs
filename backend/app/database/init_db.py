from app.database.database import engine, Base

from app.models.user import User
from app.models.workspace import Workspace
from app.models.department import Department
from app.models.team import Team
from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.models.document_permission import DocumentPermission
from app.models.task import Task
from app.models.audit_log import AuditLog
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.models.document_source import DocumentSource


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
