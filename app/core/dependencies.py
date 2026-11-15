from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import User


def require_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    user_id = request.session.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated.",
        )

    user = db.get(User, user_id)

    if user is None:
        request.session.clear()
        raise HTTPException(
            status_code=401,
            detail="User not found.",
        )

    return user