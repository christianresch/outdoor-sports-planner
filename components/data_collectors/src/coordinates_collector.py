from typing import Tuple
import requests

class CoordinatesCollector():

    def __init__(self):
        pass

    def get_coordinates(self, city_name: str) -> [Tuple[float, float]]:
        # API Documentation here: https://open-meteo.com/en/docs/geocoding-api
        if not isinstance(city_name, str):
            raise ValueError("City not found. Check your input.")

        response = requests.get(f'https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json',
                                timeout = 10)

        try:
            results = response.json()['results'][0]
        except KeyError as e:
            return None

        latitude = results['latitude']
        longitude = results['longitude']

        # Tuple as latitude, then longitude order is fairly standard and Tuples are more efficient
        return (latitude, longitude)