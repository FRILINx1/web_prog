import pytest
from unittest.mock import patch, MagicMock
from service.task_service import TaskService
from domain.task import Task
from extensions import db
from flask import Flask




@pytest.fixture
def task_service_fixture():
    return TaskService()


pytest.fixture(scope='session', autouse=True)



@pytest.fixture(scope='session', autouse=True)
def app_context():
    app = Flask('test_app')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    db.init_app(app)
    with app.app_context():
        yield app


@pytest.fixture
def mock_db_session(app_context):  # Залежить від app_context
    # Ми мокуємо шлях, який використовує TaskService: 'extensions.db.session'
    with patch('extensions.db.session') as mock_session:
        # Нам потрібно забезпечити, що методи 'add' та 'commit' є моками
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.rollback = MagicMock()

        yield mock_session

import domain.user
import domain.task

def test_create_task_success(mock_db_session, task_service_fixture):

    user_id = 1
    title = "Купити продукти"

    new_task = task_service_fixture.create_task(user_id, title)


    assert isinstance(new_task, Task)

    mock_db_session.add.assert_called_once_with(new_task)
    mock_db_session.commit.assert_called_once()

def test_create_task_validation_error(task_service_fixture):
    user_id = 1

    with pytest.raises(ValueError, match="TITLE_REQUIRED"):
        task_service_fixture.create_task(user_id, "ab")

    with pytest.raises(ValueError, match="TITLE_REQUIRED"):
        task_service_fixture.create_task(user_id, "")

    with pytest.raises(ValueError, match="TITLE_REQUIRED"):
        task_service_fixture.create_task(user_id, "   ")