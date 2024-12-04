import requests.exceptions

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
            "datetime": datetime.strptime("2024-12-03", "%Y-%m-%d"),
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
        self.air_quality_data_collector.get_air_quality_data = MagicMock()
        self.air_quality_data_collector.get_air_quality_data_by_coords = MagicMock(return_value=test_data)

        def mock_side_effect(*args):
            city = args[0]  # Assuming the first argument is the city
            if city == "NonExistentCity":
                raise ValueError(f"City {city} not found")
            elif city == "BadRequest":
                raise requests.exceptions.HTTPError("400 Client Error: Bad Request")
            elif city == "ServerError":
                raise requests.exceptions.HTTPError("500 Server Error: Internal Server Error")
            elif city == "Timeout":
                raise requests.exceptions.Timeout
            else:
                return test_data  # Return some default data for other cities

        self.air_quality_data_collector.get_air_quality_data.side_effect = mock_side_effect

    def test_get_air_quality_data(self):
        data = self.air_quality_data_collector.get_air_quality_data("TestCity")

        assert data['city'] == self.test_data['city']
        assert data['latitude'] == self.test_data['latitude']
        assert data['longitude'] == self.test_data['longitude']
        assert data['aqi'] == self.test_data['aqi']
        assert data['pm25_forecast'][0]['avg'] == self.test_data['pm25_forecast'][0]['avg']

    def test_get_air_quality_data_by_coords(self):
        data = self.air_quality_data_collector.get_air_quality_data_by_coords(latitude=31.2047372, longitude=121.4489017)

        assert data['city'] == self.test_data['city']
        assert data['latitude'] == self.test_data['latitude']
        assert data['longitude'] == self.test_data['longitude']
        assert data['aqi'] == self.test_data['aqi']
        assert data['pm25_forecast'][0]['avg'] == self.test_data['pm25_forecast'][0]['avg']

    def test_client_error(self):
        with self.assertRaises(requests.exceptions.HTTPError) as context:
            self.air_quality_data_collector.get_air_quality_data("BadRequest")
        self.assertIn("400", str(context.exception))

    def test_server_error(self):
        with self.assertRaises(requests.exceptions.HTTPError) as context:
            self.air_quality_data_collector.get_air_quality_data("ServerError")
        self.assertIn("500", str(context.exception))

    def test_timeout_handling(self):
        with self.assertRaises(requests.exceptions.Timeout) as context:
            self.air_quality_data_collector.get_air_quality_data("Timeout")

    def test_incorrect_input(self):
        with self.assertRaises(TypeError):
            self.air_quality_data_collector.get_air_quality_data(city=432)

    def test_city_not_found(self):
        with self.assertRaises(ValueError):  # Assert that the error is raised
            self.air_quality_data_collector.get_air_quality_data("NonExistentCity")  # This should raise the error

    def test_get_air_quality_data_by_coords_invalid_latitude_type(self):
        # Test for latitude as a string
        with self.assertRaises(TypeError):
            self.air_quality_data_collector.get_air_quality_data_by_coords("invalid_latitude", 121.4489017)

    def test_get_air_quality_data_by_coords_invalid_longitude_type(self):
        # Test for longitude as a string
        with self.assertRaises(TypeError):
            self.air_quality_data_collector.get_air_quality_data_by_coords(31.2047372, "invalid_longitude")

    def test_get_air_quality_data_by_coords_latitude_out_of_range(self):
        # Latitude can be max 90 degrees
        with self.assertRaises(ValueError):
            self.air_quality_data_collector.get_air_quality_data_by_coords(91, 121.4489017)  # Invalid latitude > 90

    def test_get_air_quality_data_by_coords_longitude_out_of_range(self):
        # Longitude can be max 180 degrees
        with self.assertRaises(ValueError):
            self.air_quality_data_collector.get_air_quality_data_by_coords(31.2047372, 181)  # Invalid longitude > 180

    def test_get_air_quality_data_by_coords_both_out_of_range(self):
        with self.assertRaises(ValueError):
            self.air_quality_data_collector.get_air_quality_data_by_coords(91, 181)  # Invalid latitude and longitude

    #TODO test_API_unexpected_data_format


