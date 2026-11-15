from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_user
from app.models.models import (
    Category,
    Challenge,
    ChallengeFlag,
    Submission,
    Solve,
    User,
)

router = APIRouter(
    prefix="/challenges",
    tags=["Challenge Submissions"],
)


@router.post("/{category_slug}/{challenge_slug}/submit")
def submit_flag(
    category_slug: str,
    challenge_slug: str,
    flag: str = Form(...),
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    challenge = db.scalar(
        select(Challenge)
        .join(Category)
        .where(
            Category.slug == category_slug,
            Challenge.slug == challenge_slug,
            Challenge.is_active.is_(True),
        )
    )

    if challenge is None:
        raise HTTPException(
            status_code=404,
            detail="Challenge not found.",
        )

    challenge_flag = db.scalar(
        select(ChallengeFlag).where(
            ChallengeFlag.challenge_id == challenge.id
        )
    )

    if challenge_flag is None:
        raise HTTPException(
            status_code=500,
            detail="Challenge flag is not configured.",
        )

    is_correct = flag.strip() == challenge_flag.flag

    db.add(
        Submission(
            user_id=user.id,
            challenge_id=challenge.id,
            is_correct=is_correct,
        )
    )

    if not is_correct:
        db.commit()

        return {
            "correct": False,
            "message": "Incorrect flag. Try again!",
        }

    existing_solve = db.scalar(
        select(Solve).where(
            Solve.user_id == user.id,
            Solve.challenge_id == challenge.id,
        )
    )

    if existing_solve:
        db.commit()

        return {
            "correct": True,
            "already_solved": True,
            "message": "You have already solved this challenge.",
            "points_awarded": 0,
        }

    db.add(
        Solve(
            user_id=user.id,
            challenge_id=challenge.id,
            points_awarded=challenge.points,
        )
    )

    db.commit()

    return {
        "correct": True,
        "already_solved": False,
        "message": "Congratulations! Challenge completed.",
        "points_awarded": challenge.points,
    }