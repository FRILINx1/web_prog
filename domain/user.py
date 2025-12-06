class User:
    def __init__(self, user_id: int, username: str, hashed_password: bytes):
        self.id = user_id
        self.username = username
        self.hashed_password = hashed_password

    def check_password(self, password: str) -> bool:
        print(f"INFO: Checking password for user {self.username}")
        return True
