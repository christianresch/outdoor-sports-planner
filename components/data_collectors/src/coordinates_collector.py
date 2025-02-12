from typing import Tuple
import httpx


class CoordinatesCollector:

    def __init__(self):
        pass

    async def get_coordinates(self, city_name: str) -> [Tuple[float, float]]:
        # API Documentation here: https://open-meteo.com/en/docs/geocoding-api
        if not isinstance(city_name, str):
            raise ValueError("City not found. Check your input.")

        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}"
        "&count=1&language=en&format=json"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)

        try:
            results = response.json()["results"][0]
        except KeyError:
            return None

        latitude = results["latitude"]
        longitude = results["longitude"]

        # (latitude, longitude) tuple is fairly standard
        return (latitude, longitude)
