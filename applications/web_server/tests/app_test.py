import pytest
from fastapi.testclient import TestClient
import os
import pickle
from applications.web_server.src.app import app, best_outdoor_sports_day
from loguru import logger

# No need to shut down manually as these are only simply unit tests
client = TestClient(app)

DATA_ANALYZER_API_URL = "http://localhost:8003/analyze"

current_dir = os.path.dirname(os.path.abspath(__file__))

root_dir = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir, os.pardir))

components_dir = os.path.join(root_dir, "components", "data_analyzers", "test")

mock_weather_aqi_analyzer_results_path = os.path.join(
    components_dir, "mock_weather_aqi_analyzer_results.pkl"
)
with open(mock_weather_aqi_analyzer_results_path, "rb") as file:
    mock_results = pickle.load(file)

mock_results = [
    {**item, "date": item["date"].isoformat()}  # Convert 'date' to ISO 8601 string
    for item in mock_results
]


@pytest.mark.asyncio
async def test_prediction(httpx_mock):
    logger.debug(f"Mock result: {mock_results}")
    httpx_mock.add_response(
        method="POST",
        url=DATA_ANALYZER_API_URL,
        json=mock_results,
        status_code=200,
    )
    response = await best_outdoor_sports_day(user_input="Bogota")
    logger.debug(f"Test response: {response}")

    assert response.status_code == 200
    assert str(mock_results[0]["date"]) in response.body.decode("utf-8")


def test_main_page():
    response = client.get("/")
    assert response.status_code == 200


def test_multiple_requests():
    for _ in range(100):
        response = client.get("/")
        assert response.status_code == 200
