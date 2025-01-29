from typing import TypedDict, List
from datetime import datetime
import requests
from dotenv import load_dotenv
import os
#TODO Decide whether to replicate this from Weather Data Collectr
import requests_cache
from retry_requests import retry
from sqlalchemy import lateral


class AirQualityForecast(TypedDict):
    date: datetime
    avg: float

class AirQualityData(TypedDict):
    city: str
    latitude: float
    longitude: float
    datetime: datetime
    aqi: float
    dominentpol: str
    pm25_forecast: List[AirQualityForecast]
    pm10_forecast: List[AirQualityForecast]
    o3_forecast: List[AirQualityForecast]
    uvi_forecast: List[AirQualityForecast]

class AirQualityDataCollector:

    def __init__(self):
        # Dynamically determine the absolute path to the .env file
        base_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of air_quality_data_collector.py
        env_path = os.path.join(base_dir, '../../../.env')  # Adjust relative path

        # Load the .env file
        load_dotenv(env_path)

        self.AQICN_TOKEN = os.getenv("AQICN_TOKEN")

    def get_air_quality_data(self, city: str) -> AirQualityData:
        if not isinstance(city, str):
            raise TypeError("City must be a string.")

        data = self._make_request(city)

        if not self._validate_air_quality_data(data):
            raise ValueError("Data from AQICN does not align with excpeted data format.")

        result = self._process_data(data, city=city)

        return result

    def get_air_quality_data_by_coords(self, latitude: float, longitude: float) -> AirQualityData:
        if not isinstance(latitude, float) or not isinstance(longitude, float):
            raise TypeError("Latitude and longitude must be a float.")
        elif latitude > 90 or latitude < -90:
            raise ValueError("Latitude must be a float between -90 and 90.")
        elif longitude > 180 or longitude < -180:
            raise ValueError("Latitude must be a float between -180 and 180.")

        data = self._make_request(latitude=latitude, longitude=longitude)

        if not self._validate_air_quality_data(data):
            raise ValueError("Data from AQICN does not align with excpeted data format.")

        result = self._process_data(data)

        return result

    def _make_request(self, city: str = None, latitude: float = None, longitude: float = None) -> dict:
        if city:
            url = f"http://api.waqi.info/feed/{city}/?token={self.AQICN_TOKEN}"
        elif latitude is not None and longitude is not None:
            url = f"http://api.waqi.info/feed/geo:{latitude};{longitude}/?token={self.AQICN_TOKEN}"
        else:
            raise ValueError("Either 'city' or both 'latitude' and 'longitude' must be provided")

        response = requests.get(url)

        if 400 <= response.status_code < 500:
            raise requests.exceptions.HTTPError(f"{response.status_code} Client Error")
        if response.status_code >= 500:
            raise requests.exceptions.HTTPError(f"{response.status_code} Server Error")

        try:
            data = response.json()['data']
            return data
        except KeyError as e:
            raise KeyError("The expected 'data' field is missing in the response") from e

    def _validate_air_quality_data(self, data: dict) -> bool:
        if not isinstance(data, dict):
            raise TypeError(f"Expected 'data' to be a dictionary, got {type(data).__name__}")

        keys = ['aqi', 'city', 'dominentpol', 'time', 'forecast']

        for key in keys:
            try:
                test = data[key]
            except KeyError:
                return False

        city_keys = ['geo', 'name']

        for key in city_keys:
            try:
                test = data['city'][key]
            except KeyError:
                return False

        forecast_keys = ['o3', 'pm25', 'pm10', 'uvi']

        for key in forecast_keys:
            try:
                test = data['forecast']['daily'][key]
            except KeyError:
                return False

        return True

    @staticmethod
    def _process_data(data, city: str = None) -> AirQualityData:
        if city is None:
            city = data['city']['name']

        result: AirQualityData = {'city': city,
                                  # To keep this internally consistent (AQICN for example also returns city names in local script)
                                  'latitude': data['city']['geo'][0],
                                  'longitude': data['city']['geo'][1],
                                  'datetime': datetime.now(),  # TODO Add here the time returned by the API
                                  'aqi': data['aqi'],
                                  'dominentpol': data['dominentpol']
                                  }

        pollutants = ['pm25', 'pm10', 'o3', 'uvi']

        for pollutant in pollutants:
            forecasts = []

            for element in data['forecast']['daily'][pollutant]:
                forecast: AirQualityForecast = {'avg': element['avg'],
                                                'date': datetime.strptime(element['day'], "%Y-%m-%d")}

                forecasts.append(forecast)

            result[f"{pollutant}_forecast"] = forecasts

        return result

    def process_external_data(self, data, city: str = None):
        if city is None:
            return self._process_data(data)
        else:
            return self._process_data(data, city)