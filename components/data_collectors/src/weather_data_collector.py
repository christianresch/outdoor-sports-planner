import openmeteo_requests
from openmeteo_requests.Client import OpenMeteoRequestsError
import requests_cache
from openmeteo_sdk.WeatherApiResponse import WeatherApiResponse
from retry_requests import retry
from typing import Union, TypedDict, List
from datetime import datetime
import pandas as pd

"""
API handling as described in https://open-meteo.com/en/docs
"""


class WeatherForecast(TypedDict):
    data: datetime
    weather_code: float
    temperature_2m_max: float
    sunshine_duration: float
    precipitation_hours: float


class WeatherDataCollector:

    url = "https://api.open-meteo.com/v1/forecast"

    def __init__(self):
        # Set up the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=retry_session)

    def get_weather_data(
        self,
        latitude: float,
        longitude: float,
        current: str = "temperature_2m",
        daily: [str] = [
            "weather_code",
            "temperature_2m_max",
            "sunshine_duration",
            "precipitation_hours",
        ],
        only_current: bool = False,
    ) -> Union[float, List[WeatherForecast]]:

        if not isinstance(latitude, float) or not isinstance(longitude, float):
            raise TypeError("Latitude and longitude must be a float.")
        elif latitude > 90 or latitude < -90:
            raise ValueError("Latitude must be a float between -90 and 90.")
        elif longitude > 180 or longitude < -180:
            raise ValueError("Latitude must be a float between -180 and 180.")

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": current,
            "timezone": "auto",  # Let's open-meteo automatically detect the timezone
        }

        if only_current:
            responses = self._make_request(params)

            # Process first location. Add a for-loop for multiple locations or models
            response = responses[0]

            # Current values. The order of variables needs to be the same as requested.
            current = response.Current()
            current_temperature_2m = current.Variables(0).Value()

            return current_temperature_2m

        params["daily"] = daily

        responses = self._make_request(params)

        daily_dict = self._process_data(responses)

        return daily_dict

    def _make_request(self, params: dict) -> List:
        try:
            responses = self.openmeteo.weather_api(self.url, params=params)
            return responses
        except OpenMeteoRequestsError as e:
            raise ValueError("Bad request: Check your parameters.") from e

    @staticmethod
    def _process_data(data: WeatherApiResponse) -> list[dict]:
        # Process first location. Add a for-loop for multiple locations or models
        response = data[0]

        daily = response.Daily()
        daily_weather_code = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
        daily_sunshine_duration = daily.Variables(2).ValuesAsNumpy()
        daily_precipitation_hours = daily.Variables(3).ValuesAsNumpy()

        daily_data = {
            "date": pd.date_range(
                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=daily.Interval()),
                inclusive="left",
            )
        }
        daily_data["weather_code"] = daily_weather_code
        daily_data["temperature_2m_max"] = daily_temperature_2m_max
        daily_data["sunshine_duration"] = daily_sunshine_duration
        daily_data["precipitation_hours"] = daily_precipitation_hours

        daily_dataframe = pd.DataFrame(data=daily_data)

        daily_dict = daily_dataframe.to_dict(orient="records")

        return daily_dict

    def process_external_data(self, data: WeatherApiResponse) -> list[dict]:
        return self._process_data(data)
