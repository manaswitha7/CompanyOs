from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.company import Company
from app.models.person import Person
from app.models.project import Project
from app.models.department import Department
from app.models.team import Team


router = APIRouter(
    prefix="/organization",
    tags=["Organization"],
)


# ============================================================
# PYDANTIC SCHEMAS
# ============================================================


class CompanyCreate(BaseModel):
    workspace_id: int
    name: str
    description: str | None = None
    created_by: int


class PersonCreate(BaseModel):
    workspace_id: int
    company_id: int | None = None
    name: str
    email: str | None = None
    role: str | None = None


class ProjectCreate(BaseModel):
    workspace_id: int
    company_id: int | None = None
    name: str
    description: str | None = None
    status: str = "active"
    created_by: int


class DepartmentCreate(BaseModel):
    workspace_id: int
    name: str


class TeamCreate(BaseModel):
    workspace_id: int
    department_id: int | None = None
    name: str


# ============================================================
# COMPANY
# ============================================================


@router.post("/companies")
def create_company(
    data: CompanyCreate,
    db: Session = Depends(get_db),
):
    company = Company(
        workspace_id=data.workspace_id,
        name=data.name,
        description=data.description,
        created_by=data.created_by,
        created_at=datetime.utcnow(),
    )

    db.add(company)
    db.commit()
    db.refresh(company)

    return {
        "id": company.id,
        "workspace_id": company.workspace_id,
        "name": company.name,
        "description": company.description,
        "created_by": company.created_by,
        "created_at": company.created_at,
    }


@router.get("/companies")
def list_companies(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    companies = (
        db.query(Company)
        .filter(
            Company.workspace_id == workspace_id
        )
        .order_by(
            Company.created_at.desc()
        )
        .all()
    )

    return {
        "count": len(companies),
        "companies": [
            {
                "id": company.id,
                "workspace_id": company.workspace_id,
                "name": company.name,
                "description": company.description,
                "created_by": company.created_by,
                "created_at": company.created_at,
            }
            for company in companies
        ],
    }


@router.get("/companies/{company_id}")
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
):
    company = (
        db.query(Company)
        .filter(
            Company.id == company_id
        )
        .first()
    )

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )

    return {
        "id": company.id,
        "workspace_id": company.workspace_id,
        "name": company.name,
        "description": company.description,
        "created_by": company.created_by,
        "created_at": company.created_at,
    }


# ============================================================
# PEOPLE
# ============================================================


@router.post("/people")
def create_person(
    data: PersonCreate,
    db: Session = Depends(get_db),
):
    if data.company_id is not None:
        company = (
            db.query(Company)
            .filter(
                Company.id == data.company_id
            )
            .first()
        )

        if company is None:
            raise HTTPException(
                status_code=404,
                detail="Company not found",
            )

    person = Person(
        workspace_id=data.workspace_id,
        company_id=data.company_id,
        name=data.name,
        email=data.email,
        role=data.role,
        created_at=datetime.utcnow(),
    )

    db.add(person)
    db.commit()
    db.refresh(person)

    return {
        "id": person.id,
        "workspace_id": person.workspace_id,
        "company_id": person.company_id,
        "name": person.name,
        "email": person.email,
        "role": person.role,
        "created_at": person.created_at,
    }


@router.get("/people")
def list_people(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    people = (
        db.query(Person)
        .filter(
            Person.workspace_id == workspace_id
        )
        .order_by(
            Person.created_at.desc()
        )
        .all()
    )

    return {
        "count": len(people),
        "people": [
            {
                "id": person.id,
                "workspace_id": person.workspace_id,
                "company_id": person.company_id,
                "name": person.name,
                "email": person.email,
                "role": person.role,
                "created_at": person.created_at,
            }
            for person in people
        ],
    }


@router.get("/people/{person_id}")
def get_person(
    person_id: int,
    db: Session = Depends(get_db),
):
    person = (
        db.query(Person)
        .filter(
            Person.id == person_id
        )
        .first()
    )

    if person is None:
        raise HTTPException(
            status_code=404,
            detail="Person not found",
        )

    return {
        "id": person.id,
        "workspace_id": person.workspace_id,
        "company_id": person.company_id,
        "name": person.name,
        "email": person.email,
        "role": person.role,
        "created_at": person.created_at,
    }


# ============================================================
# PROJECTS
# ============================================================


@router.post("/projects")
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
):
    if data.company_id is not None:
        company = (
            db.query(Company)
            .filter(
                Company.id == data.company_id
            )
            .first()
        )

        if company is None:
            raise HTTPException(
                status_code=404,
                detail="Company not found",
            )

    project = Project(
        workspace_id=data.workspace_id,
        company_id=data.company_id,
        name=data.name,
        description=data.description,
        status=data.status,
        created_by=data.created_by,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return {
        "id": project.id,
        "workspace_id": project.workspace_id,
        "company_id": project.company_id,
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "created_by": project.created_by,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }


@router.get("/projects")
def list_projects(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    projects = (
        db.query(Project)
        .filter(
            Project.workspace_id == workspace_id
        )
        .order_by(
            Project.created_at.desc()
        )
        .all()
    )

    return {
        "count": len(projects),
        "projects": [
            {
                "id": project.id,
                "workspace_id": project.workspace_id,
                "company_id": project.company_id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "created_by": project.created_by,
                "created_at": project.created_at,
                "updated_at": project.updated_at,
            }
            for project in projects
        ],
    }


@router.get("/projects/{project_id}")
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id
        )
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return {
        "id": project.id,
        "workspace_id": project.workspace_id,
        "company_id": project.company_id,
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "created_by": project.created_by,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }


# ============================================================
# DEPARTMENTS
# ============================================================


@router.post("/departments")
def create_department(
    data: DepartmentCreate,
    db: Session = Depends(get_db),
):
    department = Department(
        workspace_id=data.workspace_id,
        name=data.name,
        created_at=datetime.utcnow(),
    )

    db.add(department)
    db.commit()
    db.refresh(department)

    return {
        "id": department.id,
        "workspace_id": department.workspace_id,
        "name": department.name,
        "created_at": department.created_at,
    }


@router.get("/departments")
def list_departments(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    departments = (
        db.query(Department)
        .filter(
            Department.workspace_id == workspace_id
        )
        .order_by(
            Department.created_at.desc()
        )
        .all()
    )

    return {
        "count": len(departments),
        "departments": [
            {
                "id": department.id,
                "workspace_id": department.workspace_id,
                "name": department.name,
                "created_at": department.created_at,
            }
            for department in departments
        ],
    }


# ============================================================
# TEAMS
# ============================================================


@router.post("/teams")
def create_team(
    data: TeamCreate,
    db: Session = Depends(get_db),
):
    if data.department_id is not None:
        department = (
            db.query(Department)
            .filter(
                Department.id == data.department_id
            )
            .first()
        )

        if department is None:
            raise HTTPException(
                status_code=404,
                detail="Department not found",
            )

    team = Team(
        workspace_id=data.workspace_id,
        department_id=data.department_id,
        name=data.name,
        created_at=datetime.utcnow(),
    )

    db.add(team)
    db.commit()
    db.refresh(team)

    return {
        "id": team.id,
        "workspace_id": team.workspace_id,
        "department_id": team.department_id,
        "name": team.name,
        "created_at": team.created_at,
    }


@router.get("/teams")
def list_teams(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    teams = (
        db.query(Team)
        .filter(
            Team.workspace_id == workspace_id
        )
        .order_by(
            Team.created_at.desc()
        )
        .all()
    )

    return {
        "count": len(teams),
        "teams": [
            {
                "id": team.id,
                "workspace_id": team.workspace_id,
                "department_id": team.department_id,
                "name": team.name,
                "created_at": team.created_at,
            }
            for team in teams
        ],
    }


# ============================================================
# ORGANIZATION OVERVIEW
# ============================================================


@router.get("/overview")
def organization_overview(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    companies = (
        db.query(Company)
        .filter(
            Company.workspace_id == workspace_id
        )
        .count()
    )

    people = (
        db.query(Person)
        .filter(
            Person.workspace_id == workspace_id
        )
        .count()
    )

    projects = (
        db.query(Project)
        .filter(
            Project.workspace_id == workspace_id
        )
        .count()
    )

    departments = (
        db.query(Department)
        .filter(
            Department.workspace_id == workspace_id
        )
        .count()
    )

    teams = (
        db.query(Team)
        .filter(
            Team.workspace_id == workspace_id
        )
        .count()
    )

    return {
        "workspace_id": workspace_id,
        "companies": companies,
        "people": people,
        "projects": projects,
        "departments": departments,
        "teams": teams,
    }
