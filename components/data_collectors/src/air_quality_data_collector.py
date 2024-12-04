from typing import TypedDict, List
from datetime import datetime
import requests
import os
#TODO Decide whether to replicate this from Weather Data Collectr
import requests_cache
from retry_requests import retry

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
        self.AQICN_TOKEN = os.environ.get("AQICN_TOKEN")

    def get_air_quality_data(self, city: str) -> AirQualityData:
        response = requests.get(f"http://api.waqi.info/feed/{city}/?token={self.AQICN_TOKEN}")

        if response.status_code >= 400 & response.status_code < 500:
            raise requests.exceptions.HTTPError(f"{str(response.status_code)} Client Error")
        if response.status_code >= 500:
            raise requests.exceptions.HTTPError(f"{str(response.status_code)} Server Error")

        try:
            data = response.json()['data']
        except KeyError as e:
            # In case you want to add more graceful error handling
            raise e

        if not self.__validate_air_quality_data__(data):
            raise ValueError("Data from AQICN does not align with excpeted data format.")

        result: AirQualityData = {'city': city, # To keep this internally consistent (AQICN for example also returns city names in local script)
                                           'latitude': data['city']['geo'][0],
                                           'longitude': data['city']['geo'][1],
                                           'datetime': datetime.now(), #TODO Add here the time returned by the API
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

    def get_air_quality_data_by_coords(self, latitude: float, longitude: float) -> AirQualityData:
        pass

    def __validate_air_quality_data__(self, data: dict) -> bool:
        keys = ['aqi', 'city', 'dominentpol', 'time', 'forecast']

        for key in keys:
            try:
                test = data[key]
            except KeyError:
                return False

        city_keys = ['geo', 'city']

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