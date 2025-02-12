from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from loguru import logger
import os
from sqlalchemy.exc import IntegrityError
from components.data_collectors.src.air_quality_data_collector import (
    AirQualityDataCollector,
)
from components.data_collectors.src.coordinates_collector import CoordinatesCollector
from components.data_gateways.src.air_quality_data_gateway import AirQualityDataGateway


def get_collector():
    return AirQualityDataCollector()


def get_coordinates_collector():
    return CoordinatesCollector()


# For docker, read database path from environment
SQLITE_AQI_DB_PATH = os.getenv("SQLITE_AQI_DB_PATH", "sqlite:///aqi.db")


def get_aqi_data_gateway():
    return AirQualityDataGateway(db_path=SQLITE_AQI_DB_PATH)


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
    collector: AirQualityDataCollector = Depends(get_collector),
    coordinates_collector: CoordinatesCollector = Depends(get_coordinates_collector),
    aqi_data_gateway: AirQualityDataGateway = Depends(get_aqi_data_gateway),
):
    logger.info(
        f"Request received with city: "
        f"{data.city}, "
        f"latitude: {str(data.latitude)} and "
        f"longitude: {str(data.longitude)}"
    )
    try:
        data.validate()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    logger.info("Making request...")

    if data.city is not None:
        result = collector.get_air_quality_data(data.city)

        if result is None:
            coords = coordinates_collector.get_coordinates(data.city)

            if not coords:
                return None

            latitude, longitude = coords

            result = collector.get_air_quality_data_by_coords(latitude, longitude)
    else:
        result = collector.get_air_quality_data_by_coords(data.latitude, data.longitude)

    # Ensuring database exists
    aqi_data_gateway.create()

    # Storing data if it does not yet exist
    if result:
        try:
            city = result["city"]
            latitude = result["latitude"]
            longitude = result["longitude"]
            aqi = result["aqi"]
            dominentpol = result["dominentpol"]

            aqi_data_gateway.insert_air_quality_data(
                city=city,
                latitude=latitude,
                longitude=longitude,
                aqi=aqi,
                dominantpol=dominentpol,
            )
        except IntegrityError:
            pass

    logger.info("Returning data...")
    return result
