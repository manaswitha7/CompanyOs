from fastapi import APIRouter, Depends

from app.database.database import SessionLocal
from app.models.user import User
from app.services.auth.dependencies import get_current_user
from app.services.evaluation.dataset import GOLDEN_DATASET
from app.services.evaluation.evaluator import evaluate_dataset


router = APIRouter(
    prefix="/evaluation",
    tags=["Evaluation"],
)


@router.post("/run")
def run_evaluation(
    current_user: User = Depends(
        get_current_user
    ),
):
    if current_user.workspace_id is None:
        return {
            "error": (
                "User is not assigned to a workspace."
            )
        }

    db = SessionLocal()

    try:

        return evaluate_dataset(
            db=db,
            dataset=GOLDEN_DATASET,
            workspace_id=current_user.workspace_id,
        )

    finally:
        db.close()
