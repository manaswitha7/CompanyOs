from sqlalchemy.orm import Session

from app.models.user import User
from app.models.team import Team
from app.models.department import Department
from app.models.person import Person
from app.models.company import Company
from app.models.project import Project


def get_cross_team_context(
    db: Session,
    user_id: int,
    workspace_id: int,
) -> dict:
    """
    Build organizational context available to a user.

    Context hierarchy:

        User
          ↓
        Team
          ↓
        Department

    Also returns workspace-level business entities
    that can be used by downstream context retrieval.
    """

    # --------------------------------------------------
    # 1. Get current user
    # --------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.workspace_id == workspace_id,
        )
        .first()
    )

    if not user:
        return {
            "user": None,
            "team": None,
            "department": None,
            "people": [],
            "companies": [],
            "projects": [],
        }

    # --------------------------------------------------
    # 2. Resolve user's team
    # --------------------------------------------------

    team = None

    if user.team_id is not None:
        team = (
            db.query(Team)
            .filter(
                Team.id == user.team_id,
                Team.workspace_id == workspace_id,
            )
            .first()
        )

    # --------------------------------------------------
    # 3. Resolve department through team
    # --------------------------------------------------

    department = None

    if team and team.department_id is not None:
        department = (
            db.query(Department)
            .filter(
                Department.id == team.department_id,
                Department.workspace_id == workspace_id,
            )
            .first()
        )

    # --------------------------------------------------
    # 4. Workspace people
    # --------------------------------------------------

    people = (
        db.query(Person)
        .filter(
            Person.workspace_id == workspace_id,
        )
        .all()
    )

    # --------------------------------------------------
    # 5. Workspace companies
    # --------------------------------------------------

    companies = (
        db.query(Company)
        .filter(
            Company.workspace_id == workspace_id,
        )
        .all()
    )

    # --------------------------------------------------
    # 6. Workspace projects
    # --------------------------------------------------

    projects = (
        db.query(Project)
        .filter(
            Project.workspace_id == workspace_id,
        )
        .all()
    )

    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "role": user.role,
        },
        "team": (
            {
                "id": team.id,
                "name": team.name,
            }
            if team
            else None
        ),
        "department": (
            {
                "id": department.id,
                "name": department.name,
            }
            if department
            else None
        ),
        "people": [
            {
                "id": person.id,
                "name": person.name,
                "email": person.email,
                "company_id": person.company_id,
                "role": person.role,
            }
            for person in people
        ],
        "companies": [
            {
                "id": company.id,
                "name": company.name,
                "description": company.description,
            }
            for company in companies
        ],
        "projects": [
            {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "company_id": project.company_id,
            }
            for project in projects
        ],
    }
