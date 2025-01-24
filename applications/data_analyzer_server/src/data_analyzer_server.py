from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
import httpx
from components.data_analyzers.src.weather_aqi_analyzer import WeatherAQIAnalyzer

def get_analyzer():
    return WeatherAQIAnalyzer()

app = FastAPI()

# API URLs for the data collector servers
# TODO To be changed
WEATHER_API_URL = "http://localhost:8001/collect_weather_data"
AIR_QUALITY_API_URL = "http://localhost:8002/collect_air_quality_data"

# Input schema
class RequestData(BaseModel):
    latitude: float | None = None
    longitude: float | None = None
    city: str | None = None

    # Validation to ensure either city or lat/long is provided
    def validate(self):
        if not self.city and (self.latitude is None or self.longitude is None):
            raise ValueError("Either 'city' or 'latitude/longitude' must be provided.")

@app.post("/analyze")
async def analyze(
        data: RequestData,
        analyzer: WeatherAQIAnalyzer = Depends(get_analyzer)
):
    try:
        # Validate input (custom validation logic)
        data.validate()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Prepare request parameters for data collectors
    params = {
        "latitude": data.latitude,
        "longitude": data.longitude,
        "city": data.city,
    }

    #TODO Adapt this!
    async with httpx.AsyncClient() as client:
        # Fetch weather data
        weather_response = await client.get(WEATHER_API_URL, params=params)
        if weather_response.status_code != 200:
            raise HTTPException(status_code=weather_response.status_code, detail="Error fetching weather data.")
        weather_data = weather_response.json()

        # Fetch air quality data
        air_quality_response = await client.get(AIR_QUALITY_API_URL, params=params)
        if air_quality_response.status_code != 200:
            raise HTTPException(status_code=air_quality_response.status_code, detail="Error fetching air quality data.")
        air_quality_data = air_quality_response.json()

    analyzer.set_weather_forecast(weather_data)
    analyzer.set_air_quality_forecast(air_quality_data)

    result = analyzer.predict_best_outdoor_sports_day()

    return result