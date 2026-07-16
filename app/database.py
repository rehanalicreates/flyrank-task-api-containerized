"""
Database connection and table schema, using SQLAlchemy.

This is the ONLY file that knows we're using Postgres. It defines:
- `engine`: the actual connection to the database
- `SessionLocal`: how we open a "conversation" with the database per request
- `TaskORM`: the table structure (what columns `tasks` has)

Nothing in main.py, models.py, or the routes needs to import from here
directly except repository.py — that's the whole point of the repository
pattern from Week 1.
"""

from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


class TaskORM(Base):
    """The actual `tasks` table structure in Postgres."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    completed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


def init_db():
    """Create tables if they don't exist yet. Called once on app startup."""
    Base.metadata.create_all(bind=engine)
