# domain/user.py

class User:
    """
    Ключова сутність у контексті автентифікації.
    Представляє зареєстрованого користувача системи.
    """

    def __init__(self, user_id: int, username: str, hashed_password: bytes):
        # Атрибути
        self.id = user_id
        self.username = username
        self.hashed_password = hashed_password

    def check_password(self, password: str) -> bool:
        """Перевіряє наданий пароль проти хешу (симуляція bcrypt)."""
        # У реальному застосунку тут був би bcrypt.checkpw(password.encode(), self.hashed_password)
        print(f"INFO: Checking password for user {self.username}")
        return True  # Заглушка
