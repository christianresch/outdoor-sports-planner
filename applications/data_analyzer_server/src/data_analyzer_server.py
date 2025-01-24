from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from loguru import logger
import httpx
from components.data_analyzers.src.weather_aqi_analyzer import WeatherAQIAnalyzer

def get_analyzer():
    return WeatherAQIAnalyzer()

app = FastAPI()

# API URLs for the data collector servers
WEATHER_API_URL = "http://localhost:8001/collect"
AIR_QUALITY_API_URL = "http://localhost:8002/collect"

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
    logger.info(f"Request received with city: {data.city}, latitude: {str(data.latitude)} and longitude: {str(data.longitude)}")
    try:
        # Validate input (custom validation logic)
        data.validate()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if data.city == "":
        data.city = None

    # Prepare request parameters for data collectors
    params = {}

    if data.city:
        params["city"] = data.city

    if data.latitude and data.longitude:
        params["latitude"] = data.latitude
        params["longitude"] = data.longitude

    async with httpx.AsyncClient() as client:
        # Fetch weather data
        logger.info(f"Fetching weather data with params: {params}")
        weather_response = await client.post(WEATHER_API_URL, json=params)
        if weather_response.status_code != 200:
            raise HTTPException(status_code=weather_response.status_code, detail="Error fetching weather data.")
        logger.info(f"Weather data received with {weather_response.status_code} status code")
        weather_data = weather_response.json()

        # Fetch air quality data
        logger.info(f"Fetching AQI data with params: {params}")
        air_quality_response = await client.post(AIR_QUALITY_API_URL, json=params)
        if air_quality_response.status_code != 200:
            raise HTTPException(status_code=air_quality_response.status_code, detail="Error fetching air quality data.")
        logger.info(f"AQI data received with {air_quality_response.status_code} status code")
        air_quality_data = air_quality_response.json()

    analyzer.set_weather_forecast(weather_data)
    analyzer.set_air_quality_forecast(air_quality_data)

    logger.info("Analyzing results...")
    result = analyzer.predict_best_outdoor_sports_day()

    return result