import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from dotenv import load_dotenv
load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL,connect_args={"check_same_thread": False})
"""
    SQLite by default only allows one thread. FastAPI uses multiple. This disables that restriction.
"""

SessionLocal = sessionmaker(
    autocommit= False,
    autoflush = False,
    bind = engine
)

Base  = declarative_base()


def get_db():
    db = SessionLocal()
    """
        This is a FastAPI dependency. Every route that needs DB access will call this. yield means — give the session, wait for route to finish, then close.

    """
    try:
        yield db
    finally:
        db.close()


