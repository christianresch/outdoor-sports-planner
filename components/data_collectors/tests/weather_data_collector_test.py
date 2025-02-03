from components.data_collectors.src.weather_data_collector import WeatherDataCollector
import unittest
from unittest.mock import MagicMock
import os
import pickle


class TestWeatherDataCollector(unittest.TestCase):

    def setUp(self):
        self.weather_data_collector = WeatherDataCollector()
        self.weather_data_collector._make_request = MagicMock()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        weather_api_mock_current_path = os.path.join(
            current_dir, "weather_api_mock_current.pkl"
        )

        with open(weather_api_mock_current_path, "rb") as file:
            mock_weather_api_current_object = pickle.load(file)

        weather_api_mock_daily_path = os.path.join(
            current_dir, "weather_api_mock_daily.pkl"
        )

        with open(weather_api_mock_daily_path, "rb") as file:
            mock_weather_api_daily_object = pickle.load(file)

        def mock_side_effect(params: dict):
            if "daily" not in params.keys():
                return mock_weather_api_current_object
            else:
                return mock_weather_api_daily_object

        self.weather_data_collector._make_request.side_effect = mock_side_effect

    def test_real_api_call(self):
        real_weather_data_collector = WeatherDataCollector()

        current_temperature_2m = real_weather_data_collector.get_weather_data(
            4.6097, -74.0817, only_current=True
        )

        assert isinstance(current_temperature_2m, (float)), "Value is not a number"

    def test_success_current(self):
        current_temperature_2m = self.weather_data_collector.get_weather_data(
            4.6097, -74.0817, only_current=True
        )

        assert round(current_temperature_2m, 1) == 13.8

    def test_success_daily(self):
        daily_forecasts = self.weather_data_collector.get_weather_data(4.6097, -74.0817)

        forecast_day_after = daily_forecasts[1]

        assert forecast_day_after["weather_code"] == 45.0
        assert round(forecast_day_after["temperature_2m_max"], 2) == 17.42
        assert round(forecast_day_after["sunshine_duration"], 2) == 38368.69
        assert forecast_day_after["precipitation_hours"] == 0.0

    def test_get_air_quality_data_by_coords_invalid_latitude_type(self):
        # Check if ValueError is raised when providing wrong input
        with self.assertRaises(TypeError):
            self.weather_data_collector.get_weather_data("Bogota", -74.0817)

    def test_get_air_quality_data_by_coords_invalid_longitude_type(self):
        # Check if ValueError is raised when providing wrong input
        with self.assertRaises(TypeError):
            self.weather_data_collector.get_weather_data(4.6097, "Bogota")

    def test_get_air_quality_data_by_coords_latitude_out_of_range(self):
        # Latitude can be max 90 degrees
        with self.assertRaises(ValueError) as context:
            self.weather_data_collector.get_weather_data(
                91.0, 121.4489017
            )  # Invalid latitude > 90
        self.assertIn("90", str(context.exception))

    def test_get_air_quality_data_by_coords_longitude_out_of_range(self):
        # Longitude can be max 180 degrees
        with self.assertRaises(ValueError) as context:
            self.weather_data_collector.get_weather_data(
                31.2047372, 181.0
            )  # Invalid longitude > 180
        self.assertIn("180", str(context.exception))

    def test_get_air_quality_data_by_coords_both_out_of_range(self):
        with self.assertRaises(ValueError) as context:
            self.weather_data_collector.get_weather_data(
                91.0, 181.0
            )  # Invalid latitude and longitude
        self.assertIn("90", str(context.exception))
