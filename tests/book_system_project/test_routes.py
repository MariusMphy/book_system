def test_routes(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to the books database !" in response.data
