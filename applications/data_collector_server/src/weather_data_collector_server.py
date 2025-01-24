from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from loguru import logger
from components.data_collectors.src.weather_data_collector import WeatherDataCollector
from components.data_collectors.src.coordinates_collector import CoordinatesCollector

def get_collector():
    return WeatherDataCollector()

def get_coordinates_collector():
    return CoordinatesCollector()

app = FastAPI()

# Input schema
class RequestData(BaseModel):
    latitude: float | None = None
    longitude: float | None = None
    city: str | None = None

    # Validation to ensure either city or lat/long is provided
    def validate(self):
        if not self.city and (self.latitude is None or self.longitude is None):
            raise ValueError("Either 'city' or 'latitude/longitude' must be provided.")

@app.post("/collect")
async def collect(
        data: RequestData,
        collector: WeatherDataCollector = Depends(get_collector),
        coordinates_collector: CoordinatesCollector = Depends(get_coordinates_collector)
):
    logger.info(f"Request received with city: {data.city}, latitude: {str(data.latitude)} and longitude: {str(data.longitude)}")
    try:
        # Validate input (custom validation logic)
        data.validate()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if data.city is not None:
        latitude, longitude = coordinates_collector.get_coordinates(data.city)

        result = collector.get_weather_data(latitude, longitude)
    else:
        result = collector.get_weather_data(data.latitude, data.longitude)

    logger.info("Returning data...")
    return result