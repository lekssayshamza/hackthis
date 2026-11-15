from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

from app.core.database import get_db
from app.core.authentication import hash_password, verify_password
from app.core.dependencies import require_user
from app.models.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={},
    )


@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/register.html",
        context={},
    )


@router.post("/register")
def register(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    username = username.strip()

    if len(username) < 3 or len(username) > 50:
        raise HTTPException(
            status_code=400,
            detail="Username must be between 3 and 50 characters.",
        )

    if len(password) < 8 or len(password) > 128:
        raise HTTPException(
            status_code=400,
            detail="Password must be between 8 and 128 characters.",
        )

    existing_user = db.scalar(
        select(User).where(User.username == username)
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Username already exists.",
        )

    user = User(
        username=username,
        password_hash=hash_password(password),
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Username already exists.",
        )

    return {"message": "Account created successfully."}


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(User.username == username.strip())
    )

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    request.session.clear()
    request.session["user_id"] = user.id

    return {"message": "Login successful."}

@router.get("/me")
def get_current_user(
    user: User = Depends(require_user),
):
    return {
        "id": user.id,
        "username": user.username,
    }


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"message": "Logout successful."}