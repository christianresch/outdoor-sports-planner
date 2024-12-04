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
        url = ""
        API_KEY = ""
        #TODO Establish connection

    def get_air_quality_data(self, city: str) -> AirQualityData:
        pass

    def get_air_quality_data_by_coords(self, latitude: float, longitude: float) -> AirQualityData:
        pass

    def __validate_air_quality_data(self, data: dict) -> bool:
        pass