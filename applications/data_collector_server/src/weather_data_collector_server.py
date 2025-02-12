from fastapi import FastAPI, HTTPException, Depends, Response
from pydantic import BaseModel
from loguru import logger
import os
from sqlalchemy.exc import IntegrityError
from components.data_collectors.src.weather_data_collector import WeatherDataCollector
from components.data_collectors.src.coordinates_collector import CoordinatesCollector
from components.data_gateways.src.weather_data_gateway import WeatherDataGateway


def get_collector():
    return WeatherDataCollector()


def get_coordinates_collector():
    return CoordinatesCollector()


# For docker, read database path from environment
SQLITE_WEATHER_DB_PATH = os.getenv("SQLITE_WEATHER_DB_PATH", "sqlite:///weather.db")


def get_weather_data_gateway():
    return WeatherDataGateway(db_path=SQLITE_WEATHER_DB_PATH)


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
    coordinates_collector: CoordinatesCollector = Depends(get_coordinates_collector),
    weather_data_gateway: WeatherDataGateway = Depends(get_weather_data_gateway),
):
    logger.info(
        f"Request received with city: {data.city}, "
        f"latitude: {str(data.latitude)} and "
        f"longitude: {str(data.longitude)}"
    )
    try:
        data.validate()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    logger.info("Making request...")

    if data.city is not None:
        coords = await coordinates_collector.get_coordinates(data.city)

        if not coords:
            return Response(status_code=204)

        latitude, longitude = coords

        result = collector.get_weather_data(latitude, longitude)
    else:
        result = collector.get_weather_data(data.latitude, data.longitude)

    # Ensuring database exists
    weather_data_gateway.create()

    # Storing data if it does not yet exist
    if result:
        temperature = result[0]["temperature_2m_max"]

        try:
            if data.city is not None:
                coords = await coordinates_collector.get_coordinates(data.city)

                if not coords:
                    return Response(status_code=204)

                latitude, longitude = coords

                city = data.city

                weather_data_gateway.insert_weather_data(
                    city=city,
                    latitude=latitude,
                    longitude=longitude,
                    temperature=temperature,
                )
            else:
                weather_data_gateway.insert_weather_data(
                    latitude=data.latitude,
                    longitude=data.longitude,
                    temperature=temperature,
                )
        except IntegrityError:
            pass

    logger.info("Returning data...")
    return result
