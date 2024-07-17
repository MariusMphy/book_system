import pytest
from book_system_project.forms import RegisterForm
from book_system_project.models import User


@pytest.fixture
def new_user():
    return User(id=1, password='124145', email='test@example.com', name='johnytest')


@pytest.fixture
def setup_register_form(client):
    with client.application.app_context():
        form = RegisterForm(name='Test Register')
        return form