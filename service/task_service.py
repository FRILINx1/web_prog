from domain.task import Task, TaskStatus
from state import IDEMPOTENCY_STORE

from extensions import db
from typing import List, Optional


class TaskService:

    def __init__(self):
        pass

    def create_task(self, user_id: int, title: str) -> Task:
        if not title or len(title.strip()) < 3:
            raise ValueError("TITLE_REQUIRED: Title must be at least 3 characters long.")

        new_task = Task(user_id=user_id, title=title.strip())

        try:
            db.session.add(new_task)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise Exception(f"DB_SAVE_ERROR: Failed to save task via SQLAlchemy: {e}")


        return new_task

    def get_all_tasks(self, user_id: int) -> List[Task]:
        return Task.query.filter_by(user_id=user_id).order_by(Task.created_at.desc()).all()

    def delete_task(self, task_id: str, user_id: int) -> bool:
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()

        if not task:
            return False

        try:
            db.session.delete(task)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise Exception("DB_DELETE_ERROR")