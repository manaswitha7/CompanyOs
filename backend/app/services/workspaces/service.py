from typing import Any

from sqlalchemy import select

from app.models.team_view import TeamView


class WorkspaceViewService:
    """
    Service for managing workspace/team views.

    This keeps view-management logic outside the API layer.
    """

    VALID_VIEW_TYPES = {
        "table",
        "kanban",
        "calendar",
        "dashboard",
    }

    def create_view(
        self,
        db,
        workspace_id: int,
        name: str,
        view_type: str = "table",
        description: str | None = None,
        configuration: dict[str, Any] | None = None,
        team: str | None = None,
        is_default: bool = False,
    ) -> TeamView:

        if view_type not in self.VALID_VIEW_TYPES:
            raise ValueError(
                f"Invalid view type: {view_type}. "
                f"Supported types: {sorted(self.VALID_VIEW_TYPES)}"
            )

        if is_default:
            self._clear_default(
                db,
                workspace_id,
                team,
            )

        view = TeamView(
            workspace_id=workspace_id,
            name=name,
            view_type=view_type,
            description=description,
            configuration=configuration or {},
            team=team,
            is_default=is_default,
        )

        db.add(view)
        db.commit()
        db.refresh(view)

        return view

    def list_views(
        self,
        db,
        workspace_id: int,
        team: str | None = None,
        view_type: str | None = None,
    ) -> list[TeamView]:

        query = select(TeamView).where(
            TeamView.workspace_id == workspace_id
        )

        if team:
            query = query.where(
                TeamView.team == team
            )

        if view_type:
            query = query.where(
                TeamView.view_type == view_type
            )

        query = query.order_by(
            TeamView.is_default.desc(),
            TeamView.name.asc(),
        )

        return list(
            db.scalars(query).all()
        )

    def get_view(
        self,
        db,
        workspace_id: int,
        view_id: int,
    ) -> TeamView:

        view = db.scalar(
            select(TeamView).where(
                TeamView.id == view_id,
                TeamView.workspace_id == workspace_id,
            )
        )

        if not view:
            raise ValueError(
                "View not found"
            )

        return view

    def update_view(
        self,
        db,
        workspace_id: int,
        view_id: int,
        data: dict[str, Any],
    ) -> TeamView:

        view = self.get_view(
            db,
            workspace_id,
            view_id,
        )

        if "view_type" in data:
            if data["view_type"] not in self.VALID_VIEW_TYPES:
                raise ValueError(
                    f"Invalid view type: {data['view_type']}"
                )

        if data.get("is_default") is True:
            self._clear_default(
                db,
                workspace_id,
                data.get("team", view.team),
            )

        allowed_fields = {
            "name",
            "view_type",
            "description",
            "configuration",
            "team",
            "is_default",
        }

        for key, value in data.items():
            if key in allowed_fields:
                setattr(view, key, value)

        db.commit()
        db.refresh(view)

        return view

    def delete_view(
        self,
        db,
        workspace_id: int,
        view_id: int,
    ) -> None:

        view = self.get_view(
            db,
            workspace_id,
            view_id,
        )

        db.delete(view)
        db.commit()

    def _clear_default(
        self,
        db,
        workspace_id: int,
        team: str | None,
    ) -> None:

        query = select(TeamView).where(
            TeamView.workspace_id == workspace_id,
            TeamView.is_default.is_(True),
        )

        if team:
            query = query.where(
                TeamView.team == team
            )

        views = db.scalars(query).all()

        for view in views:
            view.is_default = False


workspace_view_service = WorkspaceViewService()
