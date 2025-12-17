from enum import Enum
from datetime import datetime
import uuid
from extensions import db

class TaskStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"

class Task(db.Model):
    __tablename__ = 'tasks'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default=TaskStatus.ACTIVE.value)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def mark_completed(self):
        if self.status == TaskStatus.ACTIVE.value:
            self.status = TaskStatus.COMPLETED.value
            self.updated_at = datetime.utcnow()

    def update_title(self, new_title: str):
        if new_title and new_title.strip() != self.title:
            self.title = new_title.strip()
            self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "status": self.status,
            "is_completed": self.status == TaskStatus.COMPLETED.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }