import importlib
import pkgutil

from fastapi import APIRouter
from dataclasses import dataclass
from typing import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import Category, Challenge, ChallengeFlag


@dataclass
class ChallengeDefinition:
    category_name: str
    category_slug: str
    title: str
    slug: str
    difficulty: str
    points: int
    description: str
    flag: str


CHALLENGE_REGISTRY: list[ChallengeDefinition] = []

DATABASE_INITIALIZERS: list[Callable[[], None]] = []
CHALLENGE_ROUTERS: list[APIRouter] = []


def register_challenge_router(router: APIRouter):
    if router not in CHALLENGE_ROUTERS:
        CHALLENGE_ROUTERS.append(router)


def register_challenge(challenge: ChallengeDefinition):
    CHALLENGE_REGISTRY.append(challenge)


def register_database_initializer(initializer: Callable[[], None]):
    if initializer not in DATABASE_INITIALIZERS:
        DATABASE_INITIALIZERS.append(initializer)


def initialize_challenge_databases():
    for initializer in DATABASE_INITIALIZERS:
        initializer()


def discover_challenges(package_name: str):
    package = importlib.import_module(package_name)

    for _, module_name, _ in pkgutil.walk_packages(
        package.__path__,
        prefix=f"{package_name}.",
    ):
        importlib.import_module(module_name)


def sync_challenges(db: Session):
    for definition in CHALLENGE_REGISTRY:

        category = db.scalar(
            select(Category).where(
                Category.slug == definition.category_slug
            )
        )

        if category is None:
            category = Category(
                name=definition.category_name,
                slug=definition.category_slug,
            )
            db.add(category)
            db.flush()

        challenge = db.scalar(
            select(Challenge).where(
                Challenge.category_id == category.id,
                Challenge.slug == definition.slug,
            )
        )

        if challenge is None:
            challenge = Challenge(
                category_id=category.id,
                title=definition.title,
                slug=definition.slug,
                difficulty=definition.difficulty,
                points=definition.points,
                description=definition.description,
            )
            db.add(challenge)
            db.flush()

        flag = db.scalar(
            select(ChallengeFlag).where(
                ChallengeFlag.challenge_id == challenge.id
            )
        )

        if flag is None:
            flag = ChallengeFlag(
                challenge_id=challenge.id,
                flag=definition.flag,
            )
            db.add(flag)
        else:
            flag.flag = definition.flag

    db.commit()