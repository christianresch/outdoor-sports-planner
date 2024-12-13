import openmeteo_requests
from openmeteo_requests.Client import OpenMeteoRequestsError
import requests_cache
from retry_requests import retry
from typing import Union, TypedDict, List
from datetime import datetime
import pandas as pd

# API handling as described in https://open-meteo.com/en/docs#latitude=4.6097&longitude=-74.0817&current=temperature_2m&hourly=

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
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=retry_session)

    def get_weather_data(self,
                         latitude: int,
                         longitude: int,
                         #TODO Add more current weather data
                         current: str="temperature_2m",
                         daily: [str]=["weather_code",
                                       "temperature_2m_max",
                                       "sunshine_duration",
                                       "precipitation_hours"],
                         only_current: bool = False) -> Union[float, List[WeatherForecast]]:
        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": current,
            "timezone": "auto" #Let's open-meteo automatically detect the timezone based on the coordinates
        }

        # TODO Figure out how OpenMeteo API communicate HTTP Error codes

        if only_current:
            responses = self.__make_request__(params)

            # Process first location. Add a for-loop for multiple locations or weather models
            response = responses[0]

            # Current values. The order of variables needs to be the same as requested.
            current = response.Current()
            current_temperature_2m = current.Variables(0).Value()

            return current_temperature_2m

        params['daily'] = daily

        responses = self.__make_request__(params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]

        daily = response.Daily()
        daily_weather_code = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
        daily_sunshine_duration = daily.Variables(2).ValuesAsNumpy()
        daily_precipitation_hours = daily.Variables(3).ValuesAsNumpy()

        daily_data = {"date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        )}
        daily_data["weather_code"] = daily_weather_code
        daily_data["temperature_2m_max"] = daily_temperature_2m_max
        daily_data["sunshine_duration"] = daily_sunshine_duration
        daily_data["precipitation_hours"] = daily_precipitation_hours

        daily_dataframe = pd.DataFrame(data=daily_data)

        daily_dict = daily_dataframe.to_dict(orient='records')

        return daily_dict

    def __make_request__(self, params: dict) -> List:
        try:
            responses = self.openmeteo.weather_api(self.url, params=params)
            return responses
        except OpenMeteoRequestsError as e:
            raise ValueError("Bad request: Check your parameters.") from e




