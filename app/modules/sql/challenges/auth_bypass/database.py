import os
import sqlite3
from pathlib import Path

from app.core.challenge_registry import register_database_initializer
from app.modules.sql.challenges.auth_bypass.config import FLAG


DATA_DIR = Path(
    os.getenv("CHALLENGE_DATA_DIR", "data/challenges")
) / "sql"

DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATA_DIR / "auth_bypass.db"


def initialize_database():
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        """)

        user = connection.execute(
            "SELECT id FROM users WHERE username = ?",
            ("admin",),
        ).fetchone()

        if user is None:
            connection.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                ("admin", "admin123"),
            )

        connection.execute("""
            CREATE TABLE IF NOT EXISTS admin_secrets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flag TEXT NOT NULL
            )
        """)

        secret = connection.execute(
            "SELECT id FROM admin_secrets LIMIT 1"
        ).fetchone()

        if secret is None:
            connection.execute(
                "INSERT INTO admin_secrets (flag) VALUES (?)",
                (FLAG,),
            )

        connection.commit()

    finally:
        connection.close()


register_database_initializer(initialize_database)