from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)


class Challenge(Base):
    __tablename__ = "challenges"
    __table_args__ = (
        UniqueConstraint("category_id", "slug", name="uq_category_challenge_slug"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ChallengeFlag(Base):
    __tablename__ = "challenge_flags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    challenge_id: Mapped[int] = mapped_column(
        ForeignKey("challenges.id"), unique=True, nullable=False
    )
    flag: Mapped[str] = mapped_column(String(255), nullable=False)


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    challenge_id: Mapped[int] = mapped_column(
        ForeignKey("challenges.id"), nullable=False
    )
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )


class Solve(Base):
    __tablename__ = "solves"
    __table_args__ = (
        UniqueConstraint("user_id", "challenge_id", name="uq_user_challenge_solve"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    challenge_id: Mapped[int] = mapped_column(
        ForeignKey("challenges.id"), nullable=False
    )
    points_awarded: Mapped[int] = mapped_column(Integer, nullable=False)
    solved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
