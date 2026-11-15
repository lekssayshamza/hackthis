from fastapi import APIRouter, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi import Request

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Category, Challenge

router = APIRouter(
    prefix="/sql",
    tags=["SQL Injection"],
)

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def sql_category(
    request: Request,
    db: Session = Depends(get_db),
):
    category = db.scalar(
        select(Category).where(
            Category.slug == "sql-injection"
        )
    )

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="SQL Injection category not found.",
        )

    challenges = db.scalars(
        select(Challenge).where(
            Challenge.category_id == category.id,
            Challenge.is_active.is_(True),
        )
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="challenges/sql/index.html",
        context={
            "category": category,
            "challenges": challenges,
        },
    )