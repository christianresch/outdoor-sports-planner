from components.data_analyzers.src.weather_aqi_analyzer import WeatherAQIAnalyzer
import unittest
from unittest.mock import MagicMock
import os
import pickle
from datetime import date


class TestWeatherAQIAnalyzer(unittest.TestCase):

    def setUp(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))

        mock_weather_data_path = os.path.join(current_dir, "mock_weather_data.pkl")
        with open(mock_weather_data_path, "rb") as file:
            self.mock_weather_data = pickle.load(file)

        mock_aqi_data_path_path = os.path.join(current_dir, "mock_aqi_data.pkl")
        with open(mock_aqi_data_path_path, "rb") as file:
            self.mock_aqi_data = pickle.load(file)

        mock_weather_aqi_analyzer_results_path = os.path.join(
            current_dir, "mock_weather_aqi_analyzer_results.pkl"
        )
        with open(mock_weather_aqi_analyzer_results_path, "rb") as file:
            self.mock_results = pickle.load(file)

        self.weather_aqi_analyzer = WeatherAQIAnalyzer(
            weather_forecast=self.mock_weather_data,
            air_quality_forecast=self.mock_aqi_data,
        )

        mock_today = date(2024, 12, 20)

        self.weather_aqi_analyzer._get_today = MagicMock(return_value=mock_today)

    def test_predict_outdoor_sports_day(self):
        prediction = self.weather_aqi_analyzer.predict_best_outdoor_sports_day()

        assert prediction[0]["date"] == self.mock_results[0]["date"].strftime(
            "%Y-%m-%d"
        )
        assert prediction[1]["date"] == self.mock_results[1]["date"].strftime(
            "%Y-%m-%d"
        )
        assert prediction[2]["date"] == self.mock_results[2]["date"].strftime(
            "%Y-%m-%d"
        )
