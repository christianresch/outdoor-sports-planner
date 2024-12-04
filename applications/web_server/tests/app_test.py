from fastapi.testclient import TestClient
from applications.web_server.src.app import app

# No need to shut down manually as these are only simply unit tests
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

#TODO Add test for metrics, see Production Monitoring Video (in the video they do this through the Meters library in Java