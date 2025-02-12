import httpx
from components.data_collectors.src.air_quality_data_collector import (
    AirQualityDataCollector,
    AirQualityData,
)
import unittest
from unittest.mock import AsyncMock
import json
from dotenv import load_dotenv
import os
import pytest


class TestWeatherDataCollector(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_aqicn_json_response_path = os.path.join(
            current_dir, "test_aqicn_json_response.json"
        )

        self.test_json_response: AirQualityData = self.__load_test_data__(
            test_aqicn_json_response_path
        )

        self.air_quality_data_collector = AirQualityDataCollector()
        self.air_quality_data_collector._make_request = AsyncMock()

        def mock_side_effect(*args, **kwargs):
            print("Args:", args)
            print("Kwargs:", kwargs)

            city = kwargs.get("city", args[0] if len(args) > 0 else None)

            mock_request = httpx.Request("GET", "https://example.com")
            mock_response = httpx.Response(400, request=mock_request)

            if city == "NonExistentCity":
                raise ValueError(f"City {city} not found")
            elif city == "BadRequest":
                raise httpx.HTTPStatusError(
                    "400 Client Error", request=mock_request, response=mock_response
                )
            elif city == "ServerError":
                raise httpx.HTTPStatusError(
                    "500 Server Error", request=mock_request, response=mock_response
                )
            elif city == "Timeout":
                raise httpx.TimeoutException(message="Timeout", request=mock_request)
            else:
                return self.test_json_response

        self.air_quality_data_collector._make_request.side_effect = mock_side_effect

    @pytest.mark.asyncio
    async def test_get_air_quality_data(self):
        result = await self.air_quality_data_collector.get_air_quality_data("Shanghai")

        load_dotenv("../../../.env")

        self.assertEqual(result["city"], "Shanghai")
        self.assertEqual(result["latitude"], 31.2047372)
        self.assertEqual(result["longitude"], 121.4489017)
        self.assertEqual(result["aqi"], 74)
        self.assertEqual(result["pm25_forecast"][0]["avg"], 141)

    @pytest.mark.asyncio
    async def test_get_air_quality_data_by_coords(self):
        result = await self.air_quality_data_collector.get_air_quality_data_by_coords(
            latitude=31.2047372, longitude=121.4489017
        )

        self.assertEqual(result["city"], self.test_json_response["city"]["name"])
        self.assertEqual(result["latitude"], 31.2047372)
        self.assertEqual(result["longitude"], 121.4489017)
        self.assertEqual(result["aqi"], 74)
        self.assertEqual(result["pm25_forecast"][0]["avg"], 141)

    @pytest.mark.asyncio
    async def test_client_error(self):
        with self.assertRaises(httpx.HTTPStatusError) as context:
            await self.air_quality_data_collector.get_air_quality_data("BadRequest")
        self.assertIn("400", str(context.exception))

    @pytest.mark.asyncio
    async def test_server_error(self):
        with self.assertRaises(httpx.HTTPStatusError) as context:
            await self.air_quality_data_collector.get_air_quality_data("ServerError")
        self.assertIn("500", str(context.exception))

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        with self.assertRaises(httpx.TimeoutException):
            await self.air_quality_data_collector.get_air_quality_data("Timeout")

    @pytest.mark.asyncio
    async def test_incorrect_input(self):
        with self.assertRaises(TypeError):
            await self.air_quality_data_collector.get_air_quality_data(city=432)

    @pytest.mark.asyncio
    async def test_city_not_found(self):
        with self.assertRaises(ValueError):  # Assert that the error is raised
            await self.air_quality_data_collector.get_air_quality_data(
                "NonExistentCity"
            )  # This should raise the error

    @pytest.mark.asyncio
    async def test_get_air_quality_data_by_coords_invalid_latitude_type(self):
        # Test for latitude as a string
        with self.assertRaises(TypeError):
            await self.air_quality_data_collector.get_air_quality_data_by_coords(
                "invalid_latitude", 121.4489017
            )

    @pytest.mark.asyncio
    async def test_get_air_quality_data_by_coords_invalid_longitude_type(self):
        # Test for longitude as a string
        with self.assertRaises(TypeError):
            await self.air_quality_data_collector.get_air_quality_data_by_coords(
                31.2047372, "invalid_longitude"
            )

    @pytest.mark.asyncio
    async def test_get_air_quality_data_by_coords_latitude_out_of_range(self):
        # Latitude can be max 90 degrees
        with self.assertRaises(ValueError):
            await self.air_quality_data_collector.get_air_quality_data_by_coords(
                91.0, 121.4489017
            )  # Invalid latitude > 90

    @pytest.mark.asyncio
    async def test_get_air_quality_data_by_coords_longitude_out_of_range(self):
        # Longitude can be max 180 degrees
        with self.assertRaises(ValueError):
            await self.air_quality_data_collector.get_air_quality_data_by_coords(
                31.2047372, 181.0
            )  # Invalid longitude > 180

    @pytest.mark.asyncio
    async def test_get_air_quality_data_by_coords_both_out_of_range(self):
        with self.assertRaises(ValueError):
            await self.air_quality_data_collector.get_air_quality_data_by_coords(
                91.0, 181.0
            )  # Invalid latitude and longitude

    def __load_test_data__(self, test_data: str):
        with open(test_data, "r") as file:
            return json.load(file)
