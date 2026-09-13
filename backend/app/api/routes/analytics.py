from fastapi import APIRouter
from app.database.database import SessionLocal
from app.services.analytics.service import AnalyticsService


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/{workspace_id}")
def get_workspace_analytics(
    workspace_id: int,
):
    db = SessionLocal()

    try:
        return AnalyticsService.get_workspace_analytics(
            db=db,
            workspace_id=workspace_id,
        )

    finally:
        db.close()
