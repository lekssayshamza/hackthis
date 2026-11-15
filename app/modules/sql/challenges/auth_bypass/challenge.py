import sqlite3

from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates
from app.modules.sql.challenges.auth_bypass.config import FLAG

from app.core.challenge_registry import (
    ChallengeDefinition,
    register_challenge,
    register_challenge_router,
)
from app.modules.sql.challenges.auth_bypass.database import DATABASE_PATH


challenge = ChallengeDefinition(
    category_name="SQL Injection",
    category_slug="sql-injection",
    title="Authentication Bypass",
    slug="auth-bypass",
    difficulty="Easy",
    points=100,
    description="Bypass the login mechanism using SQL injection.",
    flag=FLAG,
)

register_challenge(challenge)


router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/auth-bypass")
def auth_bypass_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="challenges/sql/auth_bypass.html",
        context={"message": None},
    )


@router.post("/auth-bypass")
def auth_bypass_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        query = (
            f"SELECT id, username FROM users "
            f"WHERE username = '{username}' "
            f"AND password = '{password}'"
        )

        user = connection.execute(query).fetchone()

        if user:
            secret = connection.execute(
                "SELECT flag FROM admin_secrets LIMIT 1"
            ).fetchone()
        else:
            secret = None

    finally:
        connection.close()

    if user:
        return templates.TemplateResponse(
            request=request,
            name="challenges/sql/auth_bypass_admin.html",
            context={
                "username": user[1],
                "flag": secret[0],
            },
        )

    return templates.TemplateResponse(
        request=request,
        name="challenges/sql/auth_bypass.html",
        context={"message": "Invalid username or password."},
    )


register_challenge_router(router)
