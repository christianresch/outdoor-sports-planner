import asyncio
import json
from contextlib import asynccontextmanager
import aio_pika
import aiormq
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from loguru import logger
import httpx
from components.data_analyzers.src.weather_aqi_analyzer import WeatherAQIAnalyzer
import os

# API URLs for the data collector servers
WEATHER_API_URL = os.getenv("WEATHER_API_URL", "http://localhost:8002/collect")

AIR_QUALITY_API_URL = os.getenv("AIR_QUALITY_API_URL", "http://localhost:8003/collect")

logger.info(f"WEATHER_API_URL is set to: {WEATHER_API_URL}")
logger.info(f"AIR_QUALITY_API_URL is set to: {AIR_QUALITY_API_URL}")

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
ANALYZER_QUEUE_NAME = os.getenv("ANALYZER_QUEUE_NAME", "data_analyzer_queue")

rabbitmq_connection = None  # Global connection pool


# Input schema
class RequestData(BaseModel):
    latitude: float | None = None
    longitude: float | None = None
    city: str | None = None

    # Validation to ensure either city or lat/long is provided
    def validate(self):
        if not self.city and (self.latitude is None or self.longitude is None):
            raise ValueError("Either 'city' or 'latitude/longitude' must be provided.")


async def get_rabbitmq_connection():
    """Get a shared RabbitMQ connection from the pool."""
    global rabbitmq_connection
    if rabbitmq_connection is None or rabbitmq_connection.is_closed:
        try:
            rabbitmq_connection = await aio_pika.connect_robust(RABBITMQ_URL)
            logger.info("Successfully connected to RabbitMQ")
        except Exception as e:
            logger.error(f"RabbitMQ connection failed: {e}")
            await asyncio.sleep(5)  # Wait before retrying
            return await get_rabbitmq_connection()  # Retry recursively
    return rabbitmq_connection


def get_analyzer():
    return WeatherAQIAnalyzer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FastAPI app starts, starts RabbitMQ consumer")
    task = asyncio.create_task(consume_from_rabbitmq())  # Background task
    yield  # App runs here
    logger.info("Shutting down RabbitMQ consumer")
    task.cancel()  # Clean up


app = FastAPI(lifespan=lifespan)


async def _analyze(data: RequestData, analyzer: WeatherAQIAnalyzer = None):
    if analyzer is None:
        analyzer = get_analyzer()

    try:
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

    async with httpx.AsyncClient(timeout=30) as client:
        # Fetch weather data
        logger.info(f"Fetching weather data with params: {params}")
        weather_response = await client.post(WEATHER_API_URL, json=params)
        if weather_response.status_code == 204:
            return {"status_code": 204, "data": None}
        elif weather_response.status_code != 200:
            raise HTTPException(
                status_code=weather_response.status_code,
                detail="Error fetching weather data.",
            )
        logger.info(
            f"Weather data received with " f"{weather_response.status_code} status code"
        )
        weather_data = weather_response.json()

        # Fetch AQI data
        logger.info(f"Fetching AQI data with params: {params}")
        air_quality_response = await client.post(AIR_QUALITY_API_URL, json=params)

        if air_quality_response.status_code == 204:
            return {"status_code": 204, "data": None}
        elif air_quality_response.status_code != 200:
            raise HTTPException(
                status_code=air_quality_response.status_code,
                detail="Error fetching air quality data.",
            )
        logger.info(
            f"AQI data received with " f"{air_quality_response.status_code} status code"
        )
        air_quality_data = air_quality_response.json()

    if not weather_data or not air_quality_data:
        return {"status_code": 204, "data": None}

    analyzer.set_weather_forecast(weather_data)
    analyzer.set_air_quality_forecast(air_quality_data)

    logger.info("Starting analysis...")
    logger.debug(f"Weather data: {analyzer.get_weather_forecast()}")
    logger.debug(f"AQI data: {analyzer.get_air_quality_forecast()}")
    result = analyzer.predict_best_outdoor_sports_day()

    logger.debug(f"Returning results: {result}")

    return {"status_code": 200, "data": result}


@app.post("/analyze")
async def analyze(
    data: RequestData, analyzer: WeatherAQIAnalyzer = Depends(get_analyzer)
):
    logger.info(
        f"HTTP request received with city: {data.city}, "
        f"latitude: {str(data.latitude)} and longitude: {str(data.longitude)}"
    )
    response = await _analyze(data=data, analyzer=analyzer)

    return JSONResponse(status_code=response["status_code"], content=response["data"])


async def process_rabbitmq_message(message: aio_pika.IncomingMessage):
    try:
        data = json.loads(message.body)

        await message.ack()

        if not isinstance(data, RequestData):
            if isinstance(data, dict):
                data = RequestData(**data)

        analyzer = get_analyzer()
        response = await _analyze(data, analyzer)

        connection = await get_rabbitmq_connection()
        channel = await connection.channel()

        # Send reply back to the response queue
        if message.reply_to:
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(response).encode(),
                    correlation_id=message.correlation_id,
                ),
                routing_key=message.reply_to,
            )
    except Exception as e:
        logger.error(f"Error processing RabbitMQ message: {e}")
        try:
            if not message.channel.is_closed:
                await message.nack(requeue=True)  # Requeue message
            else:
                logger.error("Cannot nack message: Channel is closed")
        except aiormq.exceptions.ChannelInvalidStateError:
            logger.error("Channel was already closed, cannot nack message")


async def consume_from_rabbitmq():
    connection = await get_rabbitmq_connection()
    channel = await connection.channel()
    queue = await channel.declare_queue(ANALYZER_QUEUE_NAME, durable=True)
    await queue.consume(process_rabbitmq_message)

    logger.info("Waiting for RabbitMQ messages")
    await asyncio.Future()
