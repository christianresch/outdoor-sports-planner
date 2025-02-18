import aio_pika
import json
import asyncio
import uuid
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from loguru import logger
import httpx
from prometheus_fastapi_instrumentator import Instrumentator
import os

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(__file__))
templates_path = os.path.join(current_dir, "templates")
templates = Jinja2Templates(directory=templates_path)

Instrumentator().instrument(app).expose(app)

DATA_ANALYZER_URL = os.getenv("DATA_ANALYZER_URL", "http://localhost:8001/analyze")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
USE_RABBITMQ = os.getenv("USE_RABBITMQ", "false").lower() == "true"
ANALYZER_QUEUE_NAME = os.getenv("ANALYZER_QUEUE_NAME", "data_analyzer_queue")
RESPONSE_QUEUE = os.getenv("RESPONSE_QUEUE", "response_queue")

rabbitmq_connection = None


async def get_rabbitmq_connection():
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


async def _publish_to_queue(message: dict):
    connection = await get_rabbitmq_connection()
    async with connection:
        channel = await connection.channel()

        response_queue = await channel.declare_queue(RESPONSE_QUEUE, durable=True)

        correlation_id = str(uuid.uuid4())

        # Publish the request with reply_to queue
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                correlation_id=correlation_id,
                reply_to=response_queue.name,
            ),
            routing_key=ANALYZER_QUEUE_NAME,
        )

        # TODO It might make sense to add asyncio.Future here

        try:
            async with response_queue.iterator() as queue_iter:
                async for response in queue_iter:
                    logger.info(
                        f"Web Server received message: {response.body.decode()}"
                    )
                    if response.correlation_id == correlation_id:
                        logger.info("Web Server processing correct correlation_id")

                        await response.ack()
                        logger.info("Web Server ACKNOWLEDGED message")

                        decoded_response = json.loads(response.body.decode())
                        return decoded_response
        except asyncio.TimeoutError:
            return {"status_code": 504, "data": None}
        except Exception:
            return {"status_code": 500, "data": None}


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.post("/best_outdoor_sports_day", response_class=HTMLResponse)
async def best_outdoor_sports_day(request: Request, user_input: str = Form(...)):
    user_input = user_input.capitalize()

    logger.info(f"Request received with {user_input}")

    params = {}
    params["city"] = user_input

    if USE_RABBITMQ:
        logger.info(f"Fetching best sports day via RabbitMQ with params: {params}")
        data_analyzer_response = await _publish_to_queue(params)

        logger.debug(f"Received response message: {data_analyzer_response}")

        if data_analyzer_response["status_code"] == 204:
            return templates.TemplateResponse(request, "prediction_unavailable.html")
        elif data_analyzer_response["status_code"] != 200:
            return templates.TemplateResponse(request, "prediction_unavailable.html")
        logger.info(
            f"Best sports day received with "
            f"{data_analyzer_response['status_code']} status code"
        )
        data_analyzer_response = data_analyzer_response["data"]
    else:
        async with httpx.AsyncClient() as client:
            logger.info(f"Fetching best sports day via httpx with params: {params}")
            data_analyzer_response = await client.post(DATA_ANALYZER_URL, json=params)
            if data_analyzer_response.status_code == 204:
                return templates.TemplateResponse(
                    request, "prediction_unavailable.html"
                )
            elif data_analyzer_response.status_code != 200:
                raise HTTPException(
                    status_code=data_analyzer_response.status_code,
                    detail="Error fetching best sports day.",
                )
            logger.info(
                f"Best sports day received with "
                f"{data_analyzer_response.status_code} status code"
            )
        data_analyzer_response = data_analyzer_response.json()

    logger.debug(f"Best sports day received with {data_analyzer_response}")

    # Analyzer gives a None result if no forecasts or the location cannot be found.
    if not data_analyzer_response:
        return templates.TemplateResponse(request, "prediction_unavailable.html")

    return templates.TemplateResponse(
        request=request,
        name="prediction.html",
        context={"user_input": user_input, "data": data_analyzer_response},
    )


@app.get("/health-check")
def health_check():
    return {"status": "ok"}


@app.middleware("http")
async def log_requests(request, call_next):
    response = await call_next(request)
    logger.info(
        f"Request: {request.method} {request.url} - "
        f"Response: {response.status_code}"
    )
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Error: {str(exc)}")
    return JSONResponse(status_code=500, content={"message": "Internal Server Error"})
