from extensions import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False) # Зберігаємо хеш як рядок

    # Зв'язок з завданнями
    tasks_list = db.relationship('Task', backref='owner', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'