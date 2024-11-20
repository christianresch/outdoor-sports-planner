import requests

class WeatherDataCollector:

    def __init__(self):
        pass

    def get_weather_data(self, longitude, latitude):
        # Uses as a standard the open-meteo API: https://open-meteo.com/en/docs
        response = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m')

        #TODO Improve error handling if the REST API does not respond

        if response.status_code >= 400:
            return None
        else:
            data = response.json()
            return data