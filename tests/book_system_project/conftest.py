import pytest
from book_system_project import create_app
from book_system_project.models import db


@pytest.fixture
def client():

    app = create_app('app_testing_config.py')

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            # db.drop_all()

# pytest --cov=book_system_project tests/book_system_project/
# pytest --cov=book_system_project tests/
