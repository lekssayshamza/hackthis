import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.modules.submissions import router as submissions_router
from app.modules.progress import router as progress_router

from app.core.database import SessionLocal
from app.core.challenge_registry import (
    CHALLENGE_ROUTERS,
    discover_challenges,
    sync_challenges,
    initialize_challenge_databases,
)
from app.modules.auth import router as auth_router
from app.modules.sql.router import router as sql_router

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Category


discover_challenges("app.modules.sql.challenges")


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()

    try:
        sync_challenges(db)
    finally:
        db.close()

    initialize_challenge_databases()

    yield


app = FastAPI(title="hackthis", lifespan=lifespan)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

templates = Jinja2Templates(directory="app/templates")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "development-secret-change-me"),
    same_site="lax",
    https_only=os.getenv("COOKIE_HTTPS_ONLY", "false").lower() == "true",
    max_age=3600,
)

app.include_router(auth_router)
app.include_router(sql_router)
app.include_router(submissions_router)
app.include_router(progress_router)

for challenge_router in CHALLENGE_ROUTERS:
    app.include_router(challenge_router, prefix="/sql")


@app.get("/")
def home(
    request: Request,
    db: Session = Depends(get_db),
):
    categories = db.scalars(
        select(Category).order_by(Category.name)
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"categories": categories},
    )