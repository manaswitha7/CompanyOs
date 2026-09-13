from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.database.database import SessionLocal
from app.services.reports.service import ReportService


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


class ReportCreate(BaseModel):
    workspace_id: int
    title: str = Field(min_length=1, max_length=255)
    report_type: str = Field(min_length=1, max_length=100)
    created_by: int

    summary: str | None = None
    metrics: dict | None = None
    insights: list | None = None
    recommendations: list | None = None


@router.post("")
def create_report(request: ReportCreate):
    db = SessionLocal()

    try:
        report = ReportService.create_report(
            db=db,
            workspace_id=request.workspace_id,
            title=request.title,
            report_type=request.report_type,
            created_by=request.created_by,
            summary=request.summary,
            metrics=request.metrics,
            insights=request.insights,
            recommendations=request.recommendations,
        )

        return {
            "id": report.id,
            "workspace_id": report.workspace_id,
            "title": report.title,
            "report_type": report.report_type,
            "summary": report.summary,
            "metrics": report.metrics,
            "insights": report.insights,
            "recommendations": report.recommendations,
            "created_by": report.created_by,
            "created_at": report.created_at,
        }

    finally:
        db.close()


@router.get("/{workspace_id}")
def list_reports(workspace_id: int):
    db = SessionLocal()

    try:
        reports = ReportService.list_reports(
            db=db,
            workspace_id=workspace_id,
        )

        return [
            {
                "id": report.id,
                "workspace_id": report.workspace_id,
                "title": report.title,
                "report_type": report.report_type,
                "summary": report.summary,
                "metrics": report.metrics,
                "insights": report.insights,
                "recommendations": report.recommendations,
                "created_by": report.created_by,
                "created_at": report.created_at,
            }
            for report in reports
        ]

    finally:
        db.close()


@router.get("/{workspace_id}/{report_id}")
def get_report(
    workspace_id: int,
    report_id: int,
):
    db = SessionLocal()

    try:
        report = ReportService.get_report(
            db=db,
            workspace_id=workspace_id,
            report_id=report_id,
        )

        if not report:
            raise HTTPException(
                status_code=404,
                detail="Report not found",
            )

        return {
            "id": report.id,
            "workspace_id": report.workspace_id,
            "title": report.title,
            "report_type": report.report_type,
            "summary": report.summary,
            "metrics": report.metrics,
            "insights": report.insights,
            "recommendations": report.recommendations,
            "created_by": report.created_by,
            "created_at": report.created_at,
        }

    finally:
        db.close()


@router.delete("/{workspace_id}/{report_id}")
def delete_report(
    workspace_id: int,
    report_id: int,
):
    db = SessionLocal()

    try:
        deleted = ReportService.delete_report(
            db=db,
            workspace_id=workspace_id,
            report_id=report_id,
        )

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Report not found",
            )

        return {
            "message": "Report deleted successfully",
            "report_id": report_id,
        }

    finally:
        db.close()
