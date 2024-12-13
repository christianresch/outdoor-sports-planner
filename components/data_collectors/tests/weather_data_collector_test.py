from components.data_collectors.src.weather_data_collector import WeatherDataCollector
import unittest
from unittest.mock import MagicMock
import os
import pickle

class TestWeatherDataCollector(unittest.TestCase):

    def setUp(self):
        self.weather_data_collector = WeatherDataCollector()
        self.weather_data_collector.__make_request__ = MagicMock()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        weather_api_mock_current_path = os.path.join(current_dir, 'weather_api_mock_current.pkl')

        with open(weather_api_mock_current_path, "rb") as file:
            mock_weather_api_current_object = pickle.load(file)

        weather_api_mock_daily_path = os.path.join(current_dir, 'weather_api_mock_daily.pkl')

        with open(weather_api_mock_daily_path, "rb") as file:
            mock_weather_api_daily_object = pickle.load(file)

        def mock_side_effect(params: dict):
            if "daily" not in params.keys():
                return mock_weather_api_current_object
            else:
                return mock_weather_api_daily_object

        self.weather_data_collector.__make_request__.side_effect = mock_side_effect


    def test_success_current(self):
        current_temperature_2m = self.weather_data_collector.get_weather_data(4.6097, -74.0817, only_current=True)

        assert round(current_temperature_2m, 1) == 13.8

    def test_real_api_call(self):
        real_weather_data_collector = WeatherDataCollector()

        current_temperature_2m = real_weather_data_collector.get_weather_data(4.6097, -74.0817, only_current=True)

        assert isinstance(current_temperature_2m, (float)), "Value is not a number"

    #TODO Write tests for querying forecasts as well
    # Note: Open the daily mock object separately to extract the data to test against

    #TODO Fix this test
    def test_wrong_user_input(self):
        self.weather_data_collector.get_weather_data.side_effect = ValueError("Invalid input: Check your parameters.")

        #Check if ValueError is raised when providing wrong input
        with self.assertRaises(ValueError) as context:
            self.weather_data_collector.get_weather_data("Bogota", -74.0817)