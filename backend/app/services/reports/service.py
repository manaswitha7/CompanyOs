from sqlalchemy.orm import Session

from app.models.report import Report


class ReportService:

    @staticmethod
    def create_report(
        db: Session,
        workspace_id: int,
        title: str,
        report_type: str,
        created_by: int,
        summary: str | None = None,
        metrics: dict | None = None,
        insights: list | None = None,
        recommendations: list | None = None,
    ) -> Report:

        report = Report(
            workspace_id=workspace_id,
            title=title,
            report_type=report_type,
            summary=summary,
            metrics=metrics,
            insights=insights,
            recommendations=recommendations,
            created_by=created_by,
        )

        db.add(report)
        db.commit()
        db.refresh(report)

        return report

    @staticmethod
    def get_report(
        db: Session,
        workspace_id: int,
        report_id: int,
    ) -> Report | None:

        return (
            db.query(Report)
            .filter(
                Report.id == report_id,
                Report.workspace_id == workspace_id,
            )
            .first()
        )

    @staticmethod
    def list_reports(
        db: Session,
        workspace_id: int,
    ) -> list[Report]:

        return (
            db.query(Report)
            .filter(
                Report.workspace_id == workspace_id,
            )
            .order_by(
                Report.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def delete_report(
        db: Session,
        workspace_id: int,
        report_id: int,
    ) -> bool:

        report = (
            db.query(Report)
            .filter(
                Report.id == report_id,
                Report.workspace_id == workspace_id,
            )
            .first()
        )

        if not report:
            return False

        db.delete(report)
        db.commit()

        return True
