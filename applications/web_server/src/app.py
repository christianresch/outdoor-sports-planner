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


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.post("/best_outdoor_sports_day", response_class=HTMLResponse)
async def best_outdoor_sports_day(request: Request, user_input: str = Form(...)):
    user_input = user_input.capitalize()

    logger.info(f"Request received with {user_input}")

    params = {}
    params["city"] = user_input

    async with httpx.AsyncClient() as client:
        logger.info(f"Fetching best sports day with params: {params}")
        data_analyzer_response = await client.post(DATA_ANALYZER_URL, json=params)
        if data_analyzer_response.status_code != 200:
            raise HTTPException(
                status_code=data_analyzer_response.status_code,
                detail="Error fetching best sports day.",
            )
        logger.info(
            f"Best sports day received with "
            f"{data_analyzer_response.status_code} status code"
        )

    logger.debug(f"Best sports day received with {data_analyzer_response}")
    data_analyzer_response = data_analyzer_response.json()

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
