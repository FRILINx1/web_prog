from domain.task import Task, TaskStatus
from state import IDEMPOTENCY_STORE
from infrastructure.database import get_db_connection
from extensions import db
from typing import List, Optional


class TaskService:

    def __init__(self):
        pass

    def create_task(self, user_id: int, title: str) -> Task:
        if not title or len(title.strip()) < 3:
            raise ValueError("TITLE_REQUIRED: Title must be at least 3 characters long.")

        new_task = Task(user_id=user_id, title=title.strip())

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO tasks (id, user_id, title, is_completed, created_at) VALUES (?, ?, ?, ?, ?)",
                (new_task.id, new_task.user_id, new_task.title,
                 new_task.status.value, new_task.created_at.isoformat())
            )
            conn.commit()
        except Exception as e:
            conn.close()
            raise Exception(f"DB_SAVE_ERROR: Failed to save task: {e}")
        finally:
            conn.close()

        return new_task
