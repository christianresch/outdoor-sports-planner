from components.data_collectors.src.coordinates_collector import CoordinatesCollector
import unittest
from unittest.mock import MagicMock
import pytest


class TestCoordinatesCollector(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.coordinates_collector = CoordinatesCollector()
        self.coordinates_collector.get_coordinates = MagicMock(
            return_value=(4.60971, -74.08175)
        )

        self.real_coordinates_collector = CoordinatesCollector()

    def test_success(self):
        latitude, longitude = self.coordinates_collector.get_coordinates("Bogota")

        assert latitude == 4.60971
        assert longitude == -74.08175

    @pytest.mark.asyncio
    async def test_real_api_call(self):
        latitude, longitude = await self.real_coordinates_collector.get_coordinates(
            "Bogota"
        )

        assert isinstance(latitude, (float)), "Value is not a number"
        assert isinstance(longitude, (float)), "Value is not a number"

    def test_wrong_user_input(self):
        self.coordinates_collector.get_coordinates.side_effect = ValueError(
            "Invalid input: Check your parameters."
        )

        # Check if ValueError is raised when providing wrong input
        with self.assertRaises(ValueError):
            self.coordinates_collector.get_coordinates(2024)

    @pytest.mark.asyncio
    async def test_wrong_user_input_with_real_api(self):
        with self.assertRaises(ValueError):
            await self.real_coordinates_collector.get_coordinates(2024)

    @pytest.mark.asyncio
    async def test_city_not_found(self):
        coords = await self.real_coordinates_collector.get_coordinates("FantasyCity")

        assert coords is None
