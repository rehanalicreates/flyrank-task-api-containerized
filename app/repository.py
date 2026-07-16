"""
Repository layer for Tasks — now backed by real Postgres instead of a dict.

This is the payoff of Week 1's architecture decision. Compare this file to
Week 1's repository.py: the METHOD NAMES are identical (create, get,
list_all, update, delete) — only what happens INSIDE them changed, from
dict operations to SQL queries via SQLAlchemy.

Because main.py only ever called these method names and never touched
storage details directly, main.py needed ZERO changes to go from
in-memory to a real database. That's the whole point of a repository
pattern: swapping storage is a one-file change.
"""

from datetime import datetime, timezone

from sqlalchemy import select

from app.database import SessionLocal, TaskORM
from app.exceptions import TaskNotFoundError
from app.models import TaskCreate, TaskUpdate


class TaskRepository:
    def create(self, data: TaskCreate) -> TaskORM:
        with SessionLocal() as session:
            task = TaskORM(
                title=data.title,
                description=data.description,
                completed=data.completed,
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            return task

    def list_all(self) -> list[TaskORM]:
        with SessionLocal() as session:
            return session.scalars(select(TaskORM).order_by(TaskORM.id)).all()

    def get(self, task_id: int) -> TaskORM:
        with SessionLocal() as session:
            task = session.get(TaskORM, task_id)
            if task is None:
                raise TaskNotFoundError(task_id)
            return task

    def update(self, task_id: int, data: TaskUpdate) -> TaskORM:
        with SessionLocal() as session:
            task = session.get(TaskORM, task_id)
            if task is None:
                raise TaskNotFoundError(task_id)

            if data.title is not None:
                task.title = data.title
            if data.description is not None:
                task.description = data.description
            if data.completed is not None:
                task.completed = data.completed
            task.updated_at = datetime.now(timezone.utc)

            session.commit()
            session.refresh(task)
            return task

    def delete(self, task_id: int) -> None:
        with SessionLocal() as session:
            task = session.get(TaskORM, task_id)
            if task is None:
                raise TaskNotFoundError(task_id)
            session.delete(task)
            session.commit()


# Single shared instance used by the API routes — same as Week 1.
task_repository = TaskRepository()
