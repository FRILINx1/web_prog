
import pytest
from unittest.mock import patch, MagicMock
from service.task_service import TaskService
from domain.task import Task
from infrastructure.database import get_db_connection



@pytest.fixture
def task_service_fixture():
    return TaskService()



@patch('service.task_service.get_db_connection')
def test_create_task_success(mock_get_db, task_service_fixture):

    user_id = 1
    title = "перевірка"

    mock_conn = MagicMock()
    mock_get_db.return_value = mock_conn


    new_task = task_service_fixture.create_task(user_id, title)

    assert isinstance(new_task, Task)


    assert new_task.title == title
    assert new_task.user_id == user_id

    mock_conn.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()



def test_create_task_validation_error(task_service_fixture):
    user_id = 1

    with pytest.raises(ValueError, match="TITLE_REQUIRED"):
        task_service_fixture.create_task(user_id, "ab")

    with pytest.raises(ValueError, match="TITLE_REQUIRED"):
        task_service_fixture.create_task(user_id, "")

    with pytest.raises(ValueError, match="TITLE_REQUIRED"):
        task_service_fixture.create_task(user_id, "   ")