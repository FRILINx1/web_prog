from domain.task import Task


# from repository.task_repository import TaskRepository  # В ідеалі, тут має бути репозиторій

class TaskService:
    """
    Шар бізнес-логіки для керування завданнями (Use Cases).
    """

    def __init__(self, task_repository=None):
        # self.repo = task_repository or TaskRepository() # Використовуємо репозиторій для БД
        pass

    def create_task(self, user_id: int, title: str) -> Task:
        """Створює нове завдання і зберігає його в БД."""
        if not title or len(title.strip()) < 3:
            raise ValueError("Title must be at least 3 characters long.")

        # Генерація UUID має бути тут, а не в роуті
        task_id = str(uuid.uuid4())
        new_task = Task(task_id=task_id, user_id=user_id, title=title.strip())

        # self.repo.save(new_task) # Зберігання у БД

        return new_task

    def get_all_tasks(self, user_id: int):
        """Отримує всі завдання для конкретного користувача."""
        # return self.repo.find_by_user_id(user_id)
        pass  # Заглушка