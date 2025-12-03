# domain/task.py

from enum import Enum

class TaskStatus(Enum):
    ACTIVE = "Active"
    COMPLETED = "Completed"

class Task:
    """
    Ключова сутність у контексті керування завданнями.
    Представляє одне завдання, що належить користувачеві.
    """
    def __init__(self, task_id: int, user_id: int, title: str, status: TaskStatus = TaskStatus.ACTIVE):
        # Атрибути
        self.id = task_id
        self.user_id = user_id  # Посилання на User з іншого контексту
        self.title = title
        self.status = status

    def mark_completed(self):
        """Змінює статус завдання на Виконано."""
        if self.status == TaskStatus.ACTIVE:
            self.status = TaskStatus.COMPLETED
            print(f"Task '{self.title}' marked as completed.")
        else:
            print(f"Task '{self.title}' is already completed.")

    def update_title(self, new_title: str):
        """Оновлює назву завдання."""
        self.title = new_title
