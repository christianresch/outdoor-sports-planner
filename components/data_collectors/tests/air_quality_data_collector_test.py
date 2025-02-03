import requests.exceptions
from components.data_collectors.src.air_quality_data_collector import (
    AirQualityDataCollector,
    AirQualityData,
)
import unittest
from unittest.mock import MagicMock
import json
from dotenv import load_dotenv


class TestWeatherDataCollector(unittest.TestCase):

    def setUp(self):
        # TODO Make this work if not run from root directory
        self.test_json_response: AirQualityData = self.__load_test_data__(
            "components/data_collectors/tests/test_aqicn_json_response.json"
        )

        self.air_quality_data_collector = AirQualityDataCollector()
        self.air_quality_data_collector._make_request = MagicMock()

        def mock_side_effect(*args, **kwargs):
            print("Args:", args)
            print("Kwargs:", kwargs)

            city = kwargs.get("city", args[0] if len(args) > 0 else None)

            if city == "NonExistentCity":
                raise ValueError(f"City {city} not found")
            elif city == "BadRequest":
                raise requests.exceptions.HTTPError("400 Client Error: Bad Request")
            elif city == "ServerError":
                raise requests.exceptions.HTTPError(
                    "500 Server Error: Internal Server Error"
                )
            elif city == "Timeout":
                raise requests.exceptions.Timeout
            else:
                return self.test_json_response

        self.air_quality_data_collector._make_request.side_effect = mock_side_effect

    def test_get_air_quality_data(self):
        result = self.air_quality_data_collector.get_air_quality_data("Shanghai")

        load_dotenv("../../../.env")

        self.assertEqual(result["city"], "Shanghai")
        self.assertEqual(result["latitude"], 31.2047372)
        self.assertEqual(result["longitude"], 121.4489017)
        self.assertEqual(result["aqi"], 74)
        self.assertEqual(result["pm25_forecast"][0]["avg"], 141)

    def test_get_air_quality_data_by_coords(self):
        result = self.air_quality_data_collector.get_air_quality_data_by_coords(
            latitude=31.2047372, longitude=121.4489017
        )

        self.assertEqual(result["city"], self.test_json_response["city"]["name"])
        self.assertEqual(result["latitude"], 31.2047372)
        self.assertEqual(result["longitude"], 121.4489017)
        self.assertEqual(result["aqi"], 74)
        self.assertEqual(result["pm25_forecast"][0]["avg"], 141)

    def test_client_error(self):
        with self.assertRaises(requests.exceptions.HTTPError) as context:
            self.air_quality_data_collector.get_air_quality_data("BadRequest")
        self.assertIn("400", str(context.exception))

    def test_server_error(self):
        with self.assertRaises(requests.exceptions.HTTPError) as context:
            self.air_quality_data_collector.get_air_quality_data("ServerError")
        self.assertIn("500", str(context.exception))

    def test_timeout_handling(self):
        with self.assertRaises(requests.exceptions.Timeout):
            self.air_quality_data_collector.get_air_quality_data("Timeout")

    def test_incorrect_input(self):
        with self.assertRaises(TypeError):
            self.air_quality_data_collector.get_air_quality_data(city=432)

    def test_city_not_found(self):
        with self.assertRaises(ValueError):  # Assert that the error is raised
            self.air_quality_data_collector.get_air_quality_data(
                "NonExistentCity"
            )  # This should raise the error

    def test_get_air_quality_data_by_coords_invalid_latitude_type(self):
        # Test for latitude as a string
        with self.assertRaises(TypeError):
            self.air_quality_data_collector.get_air_quality_data_by_coords(
                "invalid_latitude", 121.4489017
            )

    def test_get_air_quality_data_by_coords_invalid_longitude_type(self):
        # Test for longitude as a string
        with self.assertRaises(TypeError):
            self.air_quality_data_collector.get_air_quality_data_by_coords(
                31.2047372, "invalid_longitude"
            )

    def test_get_air_quality_data_by_coords_latitude_out_of_range(self):
        # Latitude can be max 90 degrees
        with self.assertRaises(ValueError):
            self.air_quality_data_collector.get_air_quality_data_by_coords(
                91.0, 121.4489017
            )  # Invalid latitude > 90

    def test_get_air_quality_data_by_coords_longitude_out_of_range(self):
        # Longitude can be max 180 degrees
        with self.assertRaises(ValueError):
            self.air_quality_data_collector.get_air_quality_data_by_coords(
                31.2047372, 181.0
            )  # Invalid longitude > 180

    def test_get_air_quality_data_by_coords_both_out_of_range(self):
        with self.assertRaises(ValueError):
            self.air_quality_data_collector.get_air_quality_data_by_coords(
                91.0, 181.0
            )  # Invalid latitude and longitude

    # TODO test_API_unexpected_data_format

    # TODO add test for over quota

    # TODO add test for proper time zone handling

    def __load_test_data__(self, test_data: str):
        with open(test_data, "r") as file:
            return json.load(file)
