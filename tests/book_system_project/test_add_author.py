import pytest
from book_system_project.forms import AuthorForm


@pytest.fixture
def setup_author_form(client):
    with client.application.app_context():
        form = AuthorForm(name='Test Author')
        return form


def test_add_author_success(setup_author_form):
    form = setup_author_form
    assert form.name.data == 'Test Author'
