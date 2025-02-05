import os
import json
import httpx
import pika
from dotenv import load_dotenv
from loguru import logger
from fastapi import HTTPException

load_dotenv()

# Get RabbitMQ URL from env (default to localhost for dev)
RABBITMQ_URL = os.getenv("CLOUDAMQP_URL", "amqp://guest:guest@localhost:5672/")
DATA_ANALYZER_API_URL = os.getenv(
    "DATA_ANALYZER_API_URL", "http://localhost:8001/analyze"
)


class DataFetcher:
    def __init__(self, use_rabbitmq: bool = True):
        """Initialize with either RabbitMQ or HTTP mode."""
        self.use_rabbitmq = use_rabbitmq

    async def fetch_best_sports_day(self, city: str):
        """Fetch data using either HTTP or RabbitMQ, depending on configuration."""
        if self.use_rabbitmq:
            return self._send_to_rabbitmq(city)
        else:
            return await self._send_via_http(city)

    async def _send_via_http(self, params: dict):
        """Send a request to the data analyzer service via HTTP."""
        async with httpx.AsyncClient() as client:
            logger.info(f"Fetching best sports day with params: {params}")
            data_analyzer_response = await client.post(
                DATA_ANALYZER_API_URL, json=params
            )
            if data_analyzer_response.status_code != 200:
                raise HTTPException(
                    status_code=data_analyzer_response.status_code,
                    detail="Error fetching best sports day.",
                )
            logger.info(
                f"Best sports day received with "
                f"{data_analyzer_response.status_code} status code"
            )

    def _send_to_rabbitmq(self, params: dict):
        """Send a request to the data analyzer via RabbitMQ."""
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        channel = connection.channel()
        queue_name = "data_analyzer_queue"

        channel.queue_declare(queue=queue_name, durable=True)

        message = json.dumps(params)
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2),
        )

        connection.close()
        return {"message": "Request sent to RabbitMQ"}
