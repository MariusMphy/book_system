import pytest
from book_system_project import create_app
from book_system_project.models import db
from book_system_project.models import User


@pytest.fixture
def client():

    app = create_app('app_testing_config.py')
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def new_user():
    return User(id=1, password='124145', email='test@example.com', name='johnytest')

# pytest --cov=book_system_project tests/book_system_project/
# pytest --cov=book_system_project tests/
