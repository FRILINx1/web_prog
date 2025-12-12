import pytest
from unittest.mock import patch, MagicMock
from service.task_service import TaskService
from domain.task import Task
from extensions import db




@pytest.fixture
def task_service_fixture():
    return TaskService()



@patch.object(db.session, 'commit')
@patch.object(db.session, 'add')
def test_create_task_success(mock_db_add, mock_db_commit, task_service_fixture):

    user_id = 1
    title = "Купити продукти"


    new_task = task_service_fixture.create_task(user_id, title)

    assert isinstance(new_task, Task)


    assert new_task.title == title
    assert new_task.user_id == user_id


    mock_db_add.assert_called_once_with(new_task)
    mock_db_commit.assert_called_once()





def test_create_task_validation_error(task_service_fixture):
    user_id = 1

    with pytest.raises(ValueError, match="TITLE_REQUIRED"):
        task_service_fixture.create_task(user_id, "ab")

    with pytest.raises(ValueError, match="TITLE_REQUIRED"):
        task_service_fixture.create_task(user_id, "")

    with pytest.raises(ValueError, match="TITLE_REQUIRED"):
        task_service_fixture.create_task(user_id, "   ")