from enum import Enum
from datetime import datetime
import uuid


class TaskStatus(Enum):

    ACTIVE = "active"
    COMPLETED = "completed"


class Task:


    def __init__(self, user_id: int, title: str,
                 task_id: str = None,
                 status: TaskStatus = TaskStatus.ACTIVE,
                 created_at: datetime = None):

        # 3
        self.id = task_id if task_id else str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.status = status
        self.created_at = created_at if created_at else datetime.now()
        self.updated_at = None

    def mark_completed(self):

        if self.status == TaskStatus.ACTIVE:
            self.status = TaskStatus.COMPLETED
            self.updated_at = datetime.now()

    def update_title(self, new_title: str):

        if new_title and new_title != self.title:
            self.title = new_title
            self.updated_at = datetime.now()

    def to_dict(self):

        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "is_completed": self.status == TaskStatus.COMPLETED,
            "created_at": self.created_at.isoformat() + "Z",
            "updated_at": self.updated_at.isoformat() + "Z" if self.updated_at else None
        }