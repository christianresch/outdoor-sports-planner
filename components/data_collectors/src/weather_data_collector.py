import openmeteo_requests
from openmeteo_requests.Client import OpenMeteoRequestsError
import requests_cache
from retry_requests import retry

# API handling as described in https://open-meteo.com/en/docs#latitude=4.6097&longitude=-74.0817&current=temperature_2m&hourly=

class WeatherDataCollector:


    def __init__(self):
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=retry_session)

    def get_weather_data(self, latitude: int, longitude: int, current: str="temperature_2m", daily: [str]=None) -> float:
        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": current
        }
        #TODO Openmeteo recommends to add timezones for forecasts
        if daily is not None:
            params['daily'] = daily

        #TODO Figure out how OpenMeteo API communicate HTTP Error codes

        try:
            responses = self.openmeteo.weather_api(url, params=params)
        except OpenMeteoRequestsError as e:
            raise ValueError("Bad request: Check your parameters.") from e

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]

        # Current values. The order of variables needs to be the same as requested.
        current = response.Current()
        current_temperature_2m = current.Variables(0).Value()

        return current_temperature_2m

        #TODO write return values for daily predicitions




