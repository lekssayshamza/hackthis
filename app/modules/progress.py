from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_user
from app.models.models import Category, Challenge, Solve, User

router = APIRouter(
    prefix="/progress",
    tags=["User Progress"],
)


@router.get("/me")
def get_my_progress(
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    total_points = db.scalar(
        select(func.coalesce(func.sum(Solve.points_awarded), 0))
        .where(Solve.user_id == user.id)
    )

    solved_challenges = db.execute(
        select(
            Challenge.title,
            Challenge.slug,
            Category.name.label("category"),
            Solve.points_awarded,
            Solve.solved_at,
        )
        .join(Solve, Solve.challenge_id == Challenge.id)
        .join(Category, Category.id == Challenge.category_id)
        .where(Solve.user_id == user.id)
        .order_by(Solve.solved_at.desc())
    ).all()

    return {
        "username": user.username,
        "total_points": total_points,
        "solved_count": len(solved_challenges),
        "solved_challenges": [
            {
                "title": challenge.title,
                "slug": challenge.slug,
                "category": challenge.category,
                "points": challenge.points_awarded,
                "solved_at": challenge.solved_at.isoformat(),
            }
            for challenge in solved_challenges
        ],
    }
