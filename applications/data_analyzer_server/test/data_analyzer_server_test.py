from datetime import date
from unittest.mock import MagicMock
import pytest
import os
import pickle
from applications.data_analyzer_server.src.data_analyzer_server import (
    get_analyzer,
    analyze,
    RequestData,
)
from loguru import logger

# Integration tests

WEATHER_API_URL = "http://localhost:8001/collect"
AIR_QUALITY_API_URL = "http://localhost:8002/collect"

current_dir = os.path.dirname(os.path.abspath(__file__))

root_dir = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir, os.pardir))

data_analyzers_dir = os.path.join(root_dir, "components", "data_analyzers", "test")

mock_weather_data_path = os.path.join(data_analyzers_dir, "mock_weather_data.pkl")
with open(mock_weather_data_path, "rb") as file:
    mock_weather_data = pickle.load(file)

mock_weather_data = [
    {**item, "date": item["date"].isoformat()} for item in mock_weather_data
]

mock_aqi_data_path_path = os.path.join(data_analyzers_dir, "mock_aqi_data.pkl")
with open(mock_aqi_data_path_path, "rb") as file:
    mock_aqi_data = pickle.load(file)

logger.debug(f"Mock AQI data: {mock_aqi_data}")

mock_aqi_data["datetime"] = mock_aqi_data["datetime"].isoformat()

pollutant_forecasts = ["pm25_forecast", "pm10_forecast", "o3_forecast", "uvi_forecast"]

for pollutant in pollutant_forecasts:
    if pollutant in mock_aqi_data and isinstance(mock_aqi_data[pollutant], list):
        mock_aqi_data[pollutant] = [
            {
                **item,
                "date": item["date"].isoformat(),
            }
            for item in mock_aqi_data[pollutant]
            if isinstance(item, dict) and "date" in item
        ]

mock_weather_aqi_analyzer_results_path = os.path.join(
    data_analyzers_dir, "mock_weather_aqi_analyzer_results.pkl"
)
with open(mock_weather_aqi_analyzer_results_path, "rb") as file:
    mock_results = pickle.load(file)

mock_results = [{**item, "date": item["date"].isoformat()} for item in mock_results]

logger.debug(f"Mock analyzer results: {mock_results}")


@pytest.mark.asyncio
async def test_analyze(httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url=WEATHER_API_URL,
        json=mock_weather_data,
        status_code=200,
    )

    httpx_mock.add_response(
        method="POST",
        url=AIR_QUALITY_API_URL,
        json=mock_aqi_data,
        status_code=200,
    )

    params = RequestData(latitude=4.7110, longitude=-74.0721)

    # Manually create an instance instead of using Depends
    analyzer_instance = get_analyzer()

    mock_today = date(2024, 12, 20)

    analyzer_instance._get_today = MagicMock(return_value=mock_today)

    response = await analyze(params, analyzer=analyzer_instance)
    logger.debug(f"Test response: {response}")

    assert mock_results[0]["date"] == str(response[0]["date"])


# Unit tests
def test_RequestData_valid():
    data = RequestData(latitude=1, longitude=2)
    data.validate()


def test_RequestData_invalid():
    lat_data = RequestData(latitude=1)

    with pytest.raises(
        ValueError, match="Either 'city' or 'latitude/longitude' must be provided."
    ):
        lat_data.validate()

    long_data = RequestData(longitude=1)

    with pytest.raises(
        ValueError, match="Either 'city' or 'latitude/longitude' must be provided."
    ):
        long_data.validate()
