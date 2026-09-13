from typing import Any

from app.database.database import SessionLocal
from app.models.workflow import Workflow


class WorkflowService:
    """
    Executes Company OS workflows.

    Flow:

        Event
          ↓
        Trigger matching
          ↓
        Condition evaluation
          ↓
        Action execution
    """

    # ========================================================
    # FIND MATCHING WORKFLOWS
    # ========================================================

    def find_matching_workflows(
        self,
        event_name: str,
        event_data: dict[str, Any],
        workspace_id: int | None = None,
    ) -> list[Workflow]:

        db = SessionLocal()

        try:
            workflows = db.query(Workflow).filter(
                Workflow.enabled.is_(True)
            )

            if workspace_id is not None:
                workflows = workflows.filter(
                    Workflow.workspace_id == workspace_id
                )

            workflows = workflows.all()

            matching = []

            for workflow in workflows:

                trigger = workflow.trigger or {}

                configured_event = trigger.get("event")

                if configured_event != event_name:
                    continue

                if self.evaluate_conditions(
                    workflow.conditions,
                    event_data,
                ):
                    matching.append(workflow)

            return matching

        finally:
            db.close()

    # ========================================================
    # CONDITION EVALUATION
    # ========================================================

    def evaluate_conditions(
        self,
        conditions: dict[str, Any] | None,
        event_data: dict[str, Any],
    ) -> bool:

        if not conditions:
            return True

        operator = conditions.get(
            "operator",
            "AND",
        ).upper()

        rules = conditions.get(
            "rules",
            [],
        )

        if not rules:
            return True

        results = []

        for rule in rules:

            field = rule.get("field")
            comparison = rule.get("operator")
            expected = rule.get("value")

            actual = event_data.get(field)

            result = self.evaluate_rule(
                actual=actual,
                operator=comparison,
                expected=expected,
            )

            results.append(result)

        if operator == "OR":
            return any(results)

        return all(results)

    # ========================================================
    # SINGLE RULE
    # ========================================================

    def evaluate_rule(
        self,
        actual: Any,
        operator: str | None,
        expected: Any,
    ) -> bool:

        if operator == "equals":
            return actual == expected

        if operator == "not_equals":
            return actual != expected

        if operator == "contains":

            if actual is None:
                return False

            return expected in actual

        if operator == "not_contains":

            if actual is None:
                return True

            return expected not in actual

        if operator == "exists":
            return actual is not None

        if operator == "not_exists":
            return actual is None

        if operator == "greater_than":
            return actual > expected

        if operator == "less_than":
            return actual < expected

        if operator == "greater_than_or_equal":
            return actual >= expected

        if operator == "less_than_or_equal":
            return actual <= expected

        return False

    # ========================================================
    # EXECUTE WORKFLOW
    # ========================================================

    def execute(
        self,
        workflow: Workflow,
        event_data: dict[str, Any],
    ) -> dict[str, Any]:

        results = []

        for action in workflow.actions or []:

            action_type = action.get("type")
            config = action.get(
                "config",
                {},
            )

            result = self.execute_action(
                action_type=action_type,
                config=config,
                event_data=event_data,
            )

            results.append(result)

        return {
            "workflow_id": workflow.id,
            "workflow": workflow.name,
            "executed": True,
            "actions": results,
        }

    # ========================================================
    # ACTION EXECUTION
    # ========================================================

    def execute_action(
        self,
        action_type: str | None,
        config: dict[str, Any],
        event_data: dict[str, Any],
    ) -> dict[str, Any]:

        if action_type == "log":

            message = config.get(
                "message",
                "Workflow action executed",
            )

            return {
                "type": "log",
                "status": "success",
                "message": message,
            }

        if action_type == "send_notification":

            message = config.get(
                "message",
                "Company OS workflow notification",
            )

            return {
                "type": "send_notification",
                "status": "queued",
                "message": message,
            }

        if action_type == "create_task":

            title = config.get(
                "title",
                "Workflow generated task",
            )

            return {
                "type": "create_task",
                "status": "queued",
                "title": title,
            }

        return {
            "type": action_type,
            "status": "unsupported",
            "message": (
                f"Unsupported workflow action: "
                f"{action_type}"
            ),
        }

    # ========================================================
    # PROCESS EVENT
    # ========================================================

    def process_event(
        self,
        event_name: str,
        event_data: dict[str, Any],
        workspace_id: int | None = None,
    ) -> list[dict[str, Any]]:

        workflows = self.find_matching_workflows(
            event_name=event_name,
            event_data=event_data,
            workspace_id=workspace_id,
        )

        results = []

        for workflow in workflows:

            result = self.execute(
                workflow=workflow,
                event_data=event_data,
            )

            results.append(result)

        return results


workflow_service = WorkflowService()
