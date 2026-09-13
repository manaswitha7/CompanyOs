from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.person import Person
from app.models.external_permission import ExternalIdentity


class EntityResolutionService:
    """
    Resolve identities from external systems to canonical Company OS
    Person records.

    Resolution order:

    1. Existing external identity
    2. Exact normalized email
    3. Exact normalized name
    4. No match

    Workspace isolation is enforced for every lookup.
    """

    # ============================================================
    # NORMALIZATION
    # ============================================================

    @staticmethod
    def normalize_email(email: str | None) -> str | None:
        if not email:
            return None

        value = email.strip().lower()

        return value or None

    @staticmethod
    def normalize_name(name: str | None) -> str | None:
        if not name:
            return None

        value = " ".join(
            name.strip().lower().split()
        )

        return value or None

    # ============================================================
    # RESOLVE
    # ============================================================

    def resolve(
        self,
        db: Session,
        workspace_id: int,
        provider: str,
        external_id: str | None = None,
        external_email: str | None = None,
        external_name: str | None = None,
        connector_id: int | None = None,
    ) -> dict[str, Any]:

        if not workspace_id:
            raise ValueError(
                "workspace_id is required."
            )

        if not provider:
            raise ValueError(
                "provider is required."
            )

        normalized_email = self.normalize_email(
            external_email
        )

        normalized_name = self.normalize_name(
            external_name
        )

        # ========================================================
        # 1. EXISTING EXTERNAL IDENTITY
        # ========================================================

        if external_id:

            identity_query = db.query(
                ExternalIdentity
            ).filter(
                ExternalIdentity.workspace_id
                == workspace_id,

                ExternalIdentity.provider
                == provider,

                ExternalIdentity.external_id
                == external_id,

                ExternalIdentity.is_active.is_(True),
            )

            if connector_id is not None:
                identity_query = identity_query.filter(
                    ExternalIdentity.connector_id
                    == connector_id
                )

            identity = identity_query.first()

            if identity and identity.user_id:

                person = self._find_person_by_user_id(
                    db=db,
                    workspace_id=workspace_id,
                    user_id=identity.user_id,
                )

                if person:
                    return self._result(
                        person=person,
                        confidence=1.0,
                        method="external_identity",
                        identity=identity,
                    )

        # ========================================================
        # 2. EXACT EMAIL MATCH
        # ========================================================

        if normalized_email:

            person = (
                db.query(Person)
                .filter(
                    Person.workspace_id
                    == workspace_id,

                    func.lower(Person.email)
                    == normalized_email,
                )
                .first()
            )

            if person:

                identity = self._upsert_identity(
                    db=db,
                    workspace_id=workspace_id,
                    provider=provider,
                    external_id=external_id,
                    external_email=external_email,
                    external_name=external_name,
                    connector_id=connector_id,
                    person=person,
                )

                db.commit()

                return self._result(
                    person=person,
                    confidence=0.98,
                    method="email",
                    identity=identity,
                )

        # ========================================================
        # 3. EXACT NORMALIZED NAME MATCH
        # ========================================================

        if normalized_name:

            people = (
                db.query(Person)
                .filter(
                    Person.workspace_id
                    == workspace_id
                )
                .all()
            )

            matching_people = [
                person
                for person in people
                if self.normalize_name(person.name)
                == normalized_name
            ]

            if len(matching_people) == 1:

                person = matching_people[0]

                identity = self._upsert_identity(
                    db=db,
                    workspace_id=workspace_id,
                    provider=provider,
                    external_id=external_id,
                    external_email=external_email,
                    external_name=external_name,
                    connector_id=connector_id,
                    person=person,
                )

                db.commit()

                return self._result(
                    person=person,
                    confidence=0.85,
                    method="name",
                    identity=identity,
                )

        # ========================================================
        # 4. NO MATCH
        # ========================================================

        return {
            "matched": False,
            "person": None,
            "confidence": 0.0,
            "method": "no_match",
            "external_identity_id": None,
        }

    # ============================================================
    # USER → PERSON
    # ============================================================

    @staticmethod
    def _find_person_by_user_id(
        db: Session,
        workspace_id: int,
        user_id: int,
    ) -> Person | None:

        # Current Person model does not expose user_id.
        #
        # Therefore we cannot safely infer a Person from a
        # Company OS User yet.
        #
        # Return None rather than guessing.

        return None

    # ============================================================
    # EXTERNAL IDENTITY
    # ============================================================

    def _upsert_identity(
        self,
        db: Session,
        workspace_id: int,
        provider: str,
        external_id: str | None,
        external_email: str | None,
        external_name: str | None,
        connector_id: int | None,
        person: Person,
    ) -> ExternalIdentity | None:

        if not external_id:
            return None

        identity = (
            db.query(ExternalIdentity)
            .filter(
                ExternalIdentity.workspace_id
                == workspace_id,

                ExternalIdentity.provider
                == provider,

                ExternalIdentity.external_id
                == external_id,
            )
            .first()
        )

        if identity:

            identity.external_email = (
                external_email
            )

            identity.external_name = (
                external_name
            )

            identity.connector_id = (
                connector_id
            )

            return identity

        # --------------------------------------------------------
        # IMPORTANT:
        # ExternalIdentity currently points to users.id,
        # while Person is a separate canonical entity.
        #
        # Therefore we store the external identity now but do
        # not incorrectly put Person.id into user_id.
        # --------------------------------------------------------

        identity = ExternalIdentity(
            workspace_id=workspace_id,
            connector_id=connector_id,
            external_id=external_id,
            external_email=external_email,
            external_name=external_name,
            provider=provider,
            user_id=None,
            is_active=True,
        )

        db.add(identity)

        return identity

    # ============================================================
    # RESULT
    # ============================================================

    @staticmethod
    def _result(
        person: Person,
        confidence: float,
        method: str,
        identity: ExternalIdentity | None,
    ) -> dict[str, Any]:

        return {
            "matched": True,

            "person": {
                "id": person.id,
                "workspace_id": person.workspace_id,
                "name": person.name,
                "email": person.email,
                "role": person.role,
                "company_id": person.company_id,
            },

            "confidence": confidence,

            "method": method,

            "external_identity_id": (
                identity.id
                if identity
                else None
            ),
        }


entity_resolution_service = (
    EntityResolutionService()
)
