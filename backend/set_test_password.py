from sqlalchemy.orm import Session

from app.database.database import engine
from app.models.user import User
from app.services.auth.security import hash_password


with Session(engine) as db:
    user = (
        db.query(User)
        .filter(User.id == 3)
        .first()
    )

    if not user:
        raise RuntimeError("User 3 not found")

    user.password_hash = hash_password("Test@12345")

    db.commit()

    print("Password updated for user 3")