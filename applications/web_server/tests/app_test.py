from fastapi.testclient import TestClient
from applications.web_server.src.app import app

# No need to shutdown manually as these are only simply unit tests
client = TestClient(app)

def test_main_page():
    response = client.get("/")
    assert response.status_code == 200
    # TODO Add further tests for main page

def test_multiple_requests():
    for _ in range(100):
        response = client.get("/")
        assert response.status_code == 200

#TODO Add further tests for new sub pages