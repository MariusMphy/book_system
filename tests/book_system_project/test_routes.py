def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to the books database !" in response.data


def test_view_books(client):
    response = client.get("/view_books")
    assert response.status_code == 200
    assert b"View all books:" in response.data


def test_all_ratings(client):
    response = client.get("/all_ratings")
    assert response.status_code == 200
    assert b"View rated books:" in response.data


def test_all_reviews(client):
    response = client.get("/all_reviews")
    assert response.status_code == 200
    assert b"All reviewed books:" in response.data


def test_all_read_listed(client):
    response = client.get("/all_read_listed")
    assert response.status_code == 200
    assert b"All read listed books:" in response.data

# def test_register(client):
#     test_user_data = {
#         'email': 'test@example.com',
#         'name': 'Test User',
#         'password': 'password',
#         'confirm_password': 'password',
#     }
#
#     response = client.post('/register', data=test_user_data, follow_redirects=True)
#
#
#     print(response.data.decode())
#
#     assert b'You have successfully registered' in response.data
#
#     from book_system_project.models import User
#     with client.application.app_context():
#         user = User.query.filter_by(email='test@example.com').first()
#         assert user is not None
#         assert user.name == 'Test User'
