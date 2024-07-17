import pytest
from unittest.mock import patch
from book_system_project.models import User
from book_system_project.routes import load_user


@pytest.fixture
def new_user():
    return User(id=1, password='124145', email='test@example.com', name='johnytest')


def test_load_user(client, new_user):
    with client.application.app_context():
        with patch('book_system_project.models.User.query.get') as mock_get:
            mock_get.return_value = new_user

            result = load_user(1)
            assert result == new_user
            mock_get.assert_called_once_with(1)
