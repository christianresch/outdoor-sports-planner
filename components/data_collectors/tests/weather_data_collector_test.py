from unittest.mock import patch
from requests.exceptions import Timeout
import pytest
from components.data_collectors.src.weather_data_collector import WeatherDataCollector

@pytest.fixture
def mock_requests_get():
    with patch('requests.get') as mock_get:
        yield mock_get

@pytest.fixture
def weather_collector():
    return WeatherDataCollector()

@patch('requests.get')
def test_success(weather_collector, mock_requests_get):
    # Define the mock response that replaces request.get
    mock_requests_get.return_value.status_code = 200
    #TODO replace the return value with something useful
    mock_requests_get.return_value.json.return_value = {"key": "value"}

    # Call the to be tested get_weather_data function
    result = weather_collector.get_weather_data(4.6097, -74.0817)

    assert result == {"key": "value"}