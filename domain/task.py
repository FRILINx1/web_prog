from enum import Enum
from datetime import datetime
import uuid
from extensions import db


class TaskStatus(Enum):

    ACTIVE = "active"
    COMPLETED = "completed"


class Task(db.Model):  # ❗ ЗМІНА: Наслідуємо від db.Model
    __tablename__ = 'tasks'

    # 1. Стовпці
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # ❗ FOREIGN KEY
    title = db.Column(db.String(255), nullable=False)

    # Зберігаємо статус як рядок
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.ACTIVE, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True)

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