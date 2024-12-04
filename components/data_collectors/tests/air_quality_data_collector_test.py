from components.data_collectors.src.air_quality_data_collector import AirQualityDataCollector, AirQualityData
from datetime import datetime
import unittest
from unittest.mock import MagicMock

class TestWeatherDataCollector(unittest.TestCase):

    def setUp(self):
        test_data: AirQualityData = {
            "city": "Shanghai",
            "latitude": 31.2047372,
            "longitude": 121.4489017,
            "datetime": datetime.now(),
            "aqi": 74.0,
            "dominentpol": "pm25",
            "pm25_forecast": [{"avg":141,"date": datetime.strptime("2024-12-03", "%Y-%m-%d")},
                              {"avg":148,"date": datetime.strptime("2024-12-04", "%Y-%m-%d")},
                              {"avg":178,"date": datetime.strptime("2024-12-05", "%Y-%m-%d")},
                              {"avg":215,"date": datetime.strptime("2024-12-06", "%Y-%m-%d")},
                              {"avg":155,"date": datetime.strptime("2024-12-07", "%Y-%m-%d")},
                              {"avg":144,"date": datetime.strptime("2024-12-08", "%Y-%m-%d")},
                              {"avg":153,"date": datetime.strptime("2024-12-09", "%Y-%m-%d")},
                              {"avg":152,"date": datetime.strptime("2024-12-10", "%Y-%m-%d")},
                              {"avg":147,"date": datetime.strptime("2024-12-11", "%Y-%m-%d")}],
            "pm10_forecast": [{"avg":47,"date": datetime.strptime("2024-12-03", "%Y-%m-%d")},
                              {"avg":51,"date": datetime.strptime("2024-12-04", "%Y-%m-%d")},
                              {"avg":75,"date": datetime.strptime("2024-12-05", "%Y-%m-%d")},
                              {"avg":100,"date": datetime.strptime("2024-12-06", "%Y-%m-%d")},
                              {"avg":59,"date": datetime.strptime("2024-12-07", "%Y-%m-%d")},
                              {"avg":56,"date": datetime.strptime("2024-12-08", "%Y-%m-%d")},
                              {"avg":56,"date": datetime.strptime("2024-12-09", "%Y-%m-%d")},
                              {"avg":54,"date": datetime.strptime("2024-12-10", "%Y-%m-%d")},
                              {"avg":54,"date": datetime.strptime("2024-12-11", "%Y-%m-%d")}],
            "o3_forecast": [{"avg":2,"date": datetime.strptime("2024-12-03", "%Y-%m-%d")},
                              {"avg":2,"date": datetime.strptime("2024-12-04", "%Y-%m-%d")},
                              {"avg":1,"date": datetime.strptime("2024-12-05", "%Y-%m-%d")},
                              {"avg":1,"date": datetime.strptime("2024-12-06", "%Y-%m-%d")},
                              {"avg":2,"date": datetime.strptime("2024-12-07", "%Y-%m-%d")},
                              {"avg":3,"date": datetime.strptime("2024-12-08", "%Y-%m-%d")},
                              {"avg":2,"date": datetime.strptime("2024-12-09", "%Y-%m-%d")},
                              {"avg":2,"date": datetime.strptime("2024-12-10", "%Y-%m-%d")}],
            "uvi_forecast": [{"avg":1,"date": datetime.strptime("2024-12-04", "%Y-%m-%d")},
                              {"avg":1,"date": datetime.strptime("2024-12-05", "%Y-%m-%d")},
                              {"avg":1,"date": datetime.strptime("2024-12-06", "%Y-%m-%d")},
                              {"avg":0,"date": datetime.strptime("2024-12-07", "%Y-%m-%d")},
                              {"avg":1,"date": datetime.strptime("2024-12-08", "%Y-%m-%d")},
                              {"avg":0,"date": datetime.strptime("2024-12-09", "%Y-%m-%d")}]
        }
        self.test_data = test_data

        self.air_quality_data_collector = AirQualityDataCollector()
        self.air_quality_data_collector.get_air_quality_data = MagicMock(return_value=test_data)
        self.air_quality_data_collector.get_air_quality_data_by_coords = MagicMock(return_value=test_data)

    def test_get_weather_data(self):
        pass

    def test_get_weather_data_by_coords(self):
        pass

    def test_wrong_input(self):
        pass

    def test_client_error(self):
        pass

    def test_server_error(self):
        pass

    def test_timeout_handling(self):
        pass

