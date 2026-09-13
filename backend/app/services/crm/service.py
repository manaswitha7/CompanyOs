from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.person import Person
from app.models.project import Project
from app.models.task import Task
from app.models.deal import Deal
from app.models.ticket import Ticket


class CRMService:
    """
    Service layer for the Company OS Super CRM.

    The CRM reuses existing Company OS entities instead
    of maintaining a separate duplicate CRM data model.
    """

    # =====================================================
    # COMPANIES
    # =====================================================

    def create_company(
        self,
        db: Session,
        workspace_id: int,
        created_by: int,
        name: str,
        description: str | None = None,
    ) -> Company:

        company = Company(
            workspace_id=workspace_id,
            created_by=created_by,
            name=name,
            description=description,
        )

        db.add(company)
        db.commit()
        db.refresh(company)

        return company

    def list_companies(
        self,
        db: Session,
        workspace_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Company]:

        stmt = (
            select(Company)
            .where(
                Company.workspace_id == workspace_id
            )
            .order_by(Company.id.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(db.scalars(stmt).all())

    def get_company(
        self,
        db: Session,
        workspace_id: int,
        company_id: int,
    ) -> Company | None:

        stmt = select(Company).where(
            Company.id == company_id,
            Company.workspace_id == workspace_id,
        )

        return db.scalar(stmt)

    # =====================================================
    # PEOPLE
    # =====================================================

    def create_person(
        self,
        db: Session,
        workspace_id: int,
        name: str,
        email: str | None = None,
        role: str | None = None,
        company_id: int | None = None,
    ) -> Person:

        person = Person(
            workspace_id=workspace_id,
            name=name,
            email=email,
            role=role,
            company_id=company_id,
        )

        db.add(person)
        db.commit()
        db.refresh(person)

        return person

    def list_people(
        self,
        db: Session,
        workspace_id: int,
        company_id: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Person]:

        stmt = select(Person).where(
            Person.workspace_id == workspace_id
        )

        if company_id is not None:
            stmt = stmt.where(
                Person.company_id == company_id
            )

        stmt = (
            stmt
            .order_by(Person.id.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(db.scalars(stmt).all())

    # =====================================================
    # PROJECTS
    # =====================================================

    def create_project(
        self,
        db: Session,
        workspace_id: int,
        created_by: int,
        name: str,
        description: str | None = None,
        company_id: int | None = None,
        status: str = "active",
    ) -> Project:

        project = Project(
            workspace_id=workspace_id,
            created_by=created_by,
            name=name,
            description=description,
            company_id=company_id,
            status=status,
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        return project

    def list_projects(
        self,
        db: Session,
        workspace_id: int,
        company_id: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Project]:

        stmt = select(Project).where(
            Project.workspace_id == workspace_id
        )

        if company_id is not None:
            stmt = stmt.where(
                Project.company_id == company_id
            )

        stmt = (
            stmt
            .order_by(Project.id.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(db.scalars(stmt).all())

    # =====================================================
    # TASKS
    # =====================================================

    def create_task(
        self,
        db: Session,
        workspace_id: int,
        created_by: int,
        title: str,
        description: str | None = None,
        status: str = "todo",
    ) -> Task:

        task = Task(
            workspace_id=workspace_id,
            created_by=created_by,
            title=title,
            description=description,
            status=status,
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        return task

    def list_tasks(
        self,
        db: Session,
        workspace_id: int,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Task]:

        stmt = select(Task).where(
            Task.workspace_id == workspace_id
        )

        if status is not None:
            stmt = stmt.where(
                Task.status == status
            )

        stmt = (
            stmt
            .order_by(Task.id.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(db.scalars(stmt).all())

    # =====================================================
    # DEALS
    # =====================================================

    def create_deal(
        self,
        db: Session,
        workspace_id: int,
        created_by: int,
        name: str,
        description: str | None = None,
        company_id: int | None = None,
        person_id: int | None = None,
        project_id: int | None = None,
        stage: str = "lead",
        status: str = "open",
        value: float | None = None,
        currency: str = "USD",
        expected_close_at: datetime | None = None,
    ) -> Deal:

        deal = Deal(
            workspace_id=workspace_id,
            created_by=created_by,
            name=name,
            description=description,
            company_id=company_id,
            person_id=person_id,
            project_id=project_id,
            stage=stage,
            status=status,
            value=value,
            currency=currency,
            expected_close_at=expected_close_at,
        )

        db.add(deal)
        db.commit()
        db.refresh(deal)

        return deal

    def list_deals(
        self,
        db: Session,
        workspace_id: int,
        company_id: int | None = None,
        stage: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Deal]:

        stmt = select(Deal).where(
            Deal.workspace_id == workspace_id
        )

        if company_id is not None:
            stmt = stmt.where(
                Deal.company_id == company_id
            )

        if stage is not None:
            stmt = stmt.where(
                Deal.stage == stage
            )

        if status is not None:
            stmt = stmt.where(
                Deal.status == status
            )

        stmt = (
            stmt
            .order_by(Deal.id.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(db.scalars(stmt).all())

    # =====================================================
    # TICKETS
    # =====================================================

    def create_ticket(
        self,
        db: Session,
        workspace_id: int,
        created_by: int,
        title: str,
        description: str | None = None,
        company_id: int | None = None,
        person_id: int | None = None,
        project_id: int | None = None,
        assigned_to: int | None = None,
        status: str = "open",
        priority: str = "medium",
        category: str | None = None,
    ) -> Ticket:

        ticket = Ticket(
            workspace_id=workspace_id,
            created_by=created_by,
            title=title,
            description=description,
            company_id=company_id,
            person_id=person_id,
            project_id=project_id,
            assigned_to=assigned_to,
            status=status,
            priority=priority,
            category=category,
        )

        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        return ticket

    def list_tickets(
        self,
        db: Session,
        workspace_id: int,
        company_id: int | None = None,
        status: str | None = None,
        priority: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Ticket]:

        stmt = select(Ticket).where(
            Ticket.workspace_id == workspace_id
        )

        if company_id is not None:
            stmt = stmt.where(
                Ticket.company_id == company_id
            )

        if status is not None:
            stmt = stmt.where(
                Ticket.status == status
            )

        if priority is not None:
            stmt = stmt.where(
                Ticket.priority == priority
            )

        stmt = (
            stmt
            .order_by(Ticket.id.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(db.scalars(stmt).all())


# Singleton used by the API layer
crm_service = CRMService()
