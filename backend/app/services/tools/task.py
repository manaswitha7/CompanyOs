from typing import Any

from app.database.database import SessionLocal
from app.models.task import Task
from app.services.tools.base import (
    BaseTool,
    ToolContext,
)


class CreateTaskTool(BaseTool):

    name = "create_task"

    description = (
        "Create a task in the authenticated user's "
        "Company OS workspace."
    )

    category = "task"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Task title",
                },
                "description": {
                    "type": "string",
                    "description": "Optional task description",
                },
            },
            "required": ["title"],
        }

    def execute(
        self,
        context: ToolContext,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:

        title = (
            arguments.get("title") or ""
        ).strip()

        description = (
            arguments.get("description") or ""
        ).strip()

        if not title:
            raise ValueError(
                "Task title cannot be empty."
            )

        if context.workspace_id is None:
            raise ValueError(
                "User is not assigned to a workspace."
            )

        if context.user_id is None:
            raise ValueError(
                "Authenticated user is required."
            )

        db = SessionLocal()

        try:

            task = Task(
                workspace_id=context.workspace_id,
                created_by=context.user_id,
                title=title,
                description=description or None,
                status="todo",
            )

            db.add(task)
            db.commit()
            db.refresh(task)

            return {
                "success": True,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "workspace_id": task.workspace_id,
                    "created_by": task.created_by,
                    "created_at": task.created_at,
                },
            }

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()
