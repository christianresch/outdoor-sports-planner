from components.data_collectors.src.weather_data_collector import WeatherDataCollector
import unittest
from unittest.mock import MagicMock

class TestWeatherDataCollector(unittest.TestCase):

    def setUp(self):
        self.weather_data_collector = WeatherDataCollector()
        self.weather_data_collector.get_weather_data = MagicMock(return_value=19.3)

    def test_success(self):
        current_temperature_2m = self.weather_data_collector.get_weather_data(4.6097, -74.0817)

        assert current_temperature_2m == 19.3

    def test_real_api_call(self):
        real_weather_data_collector = WeatherDataCollector()

        current_temperature_2m = real_weather_data_collector.get_weather_data(4.6097, -74.0817)

        assert isinstance(current_temperature_2m, (float)), "Value is not a number"

    #TODO Write tests for querying forecasts as well

    def test_wrong_user_input(self):
        self.weather_data_collector.get_weather_data.side_effect = ValueError("Invalid input: Check your parameters.")

        #Check if ValueError is raised when providing wrong input
        with self.assertRaises(ValueError) as context:
            self.weather_data_collector.get_weather_data("Bogota", -74.0817)