from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.project import Project
from app.models.deal import Deal
from app.models.ticket import Ticket
from app.models.document import Document
from app.models.platform import AIFeedback


class AnalyticsService:

    @staticmethod
    def get_workspace_analytics(
        db: Session,
        workspace_id: int,
    ):

        # ==============================
        # TASKS
        # ==============================

        task_rows = (
            db.query(
                Task.status,
                func.count(Task.id),
            )
            .filter(
                Task.workspace_id == workspace_id
            )
            .group_by(Task.status)
            .all()
        )

        tasks = {
            "total": sum(
                count for _, count in task_rows
            )
        }

        for status, count in task_rows:
            tasks[status] = count

        # ==============================
        # PROJECTS
        # ==============================

        project_rows = (
            db.query(
                Project.status,
                func.count(Project.id),
            )
            .filter(
                Project.workspace_id == workspace_id
            )
            .group_by(Project.status)
            .all()
        )

        projects = {
            "total": sum(
                count for _, count in project_rows
            )
        }

        for status, count in project_rows:
            projects[status] = count

        # ==============================
        # DEALS
        # ==============================

        deal_rows = (
            db.query(
                Deal.status,
                func.count(Deal.id),
            )
            .filter(
                Deal.workspace_id == workspace_id
            )
            .group_by(Deal.status)
            .all()
        )

        total_deal_value = (
            db.query(
                func.coalesce(
                    func.sum(Deal.value),
                    0,
                )
            )
            .filter(
                Deal.workspace_id == workspace_id
            )
            .scalar()
            or 0
        )

        deals = {
            "total": sum(
                count for _, count in deal_rows
            ),
            "total_value": float(
                total_deal_value
            ),
        }

        for status, count in deal_rows:
            deals[status] = count

        # ==============================
        # TICKETS
        # ==============================

        ticket_rows = (
            db.query(
                Ticket.status,
                func.count(Ticket.id),
            )
            .filter(
                Ticket.workspace_id == workspace_id
            )
            .group_by(Ticket.status)
            .all()
        )

        tickets = {
            "total": sum(
                count for _, count in ticket_rows
            )
        }

        for status, count in ticket_rows:
            tickets[status] = count

        # ==============================
        # DOCUMENTS
        # ==============================

        document_rows = (
            db.query(
                Document.status,
                func.count(Document.id),
            )
            .filter(
                Document.workspace_id == workspace_id
            )
            .group_by(Document.status)
            .all()
        )

        documents = {
            "total": sum(
                count for _, count in document_rows
            )
        }

        for status, count in document_rows:
            documents[status] = count

        # ==============================
        # AI FEEDBACK
        # ==============================

        feedback_rows = (
            db.query(
                AIFeedback.rating,
                func.count(AIFeedback.id),
            )
            .filter(
                AIFeedback.workspace_id == workspace_id
            )
            .group_by(AIFeedback.rating)
            .all()
        )

        feedback = {
            "total": sum(
                count for _, count in feedback_rows
            )
        }

        for rating, count in feedback_rows:
            feedback[str(rating)] = count

        average_rating = (
            db.query(
                func.avg(AIFeedback.rating)
            )
            .filter(
                AIFeedback.workspace_id == workspace_id
            )
            .scalar()
        )

        feedback["average_rating"] = (
            float(average_rating)
            if average_rating is not None
            else 0.0
        )

        # ==============================
        # FINAL RESPONSE
        # ==============================

        return {
            "workspace_id": workspace_id,
            "tasks": tasks,
            "projects": projects,
            "deals": deals,
            "tickets": tickets,
            "documents": documents,
            "feedback": feedback,
        }
