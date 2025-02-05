from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from loguru import logger
import httpx
from prometheus_fastapi_instrumentator import Instrumentator
import os

app = FastAPI()

# 1. Point Jinja2Templates to your templates folder
current_dir = os.path.dirname(os.path.abspath(__file__))
templates_path = os.path.join(current_dir, "templates")
templates = Jinja2Templates(directory=templates_path)

Instrumentator().instrument(app).expose(app)

DATA_ANALYZER_URL = os.getenv("DATA_ANALYZER_URL", "http://localhost:8001/analyze")


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse(request, "index.html")
    '''
    # TODO Move the html somewhere else
    return """
    <h1> Outdoor sports planner</h1>
    <h2> Get the best outdoor sport days based on air quality and weather forecast</h2>
    Enter your location here: <br>
    <br>
     <form action="/best_outdoor_sports_day" method="POST">
         <input name="user_input">
         <input type="submit" value="Submit!">
     </form>
     """
     '''


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

    # Analyzer gives an empty result if no forecasts or the location cannot be found.
    if len(data_analyzer_response) == 0:
        return templates.TemplateResponse(request, "prediction_unavailable.html")

    '''
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    </head>
    <body>
        <h1> Your outdoor sports prediction for {user_input}</h1>
        You are in <b>{user_input}</b>. Your best outdoor sports day in the coming
        days is {str(data_analyzer_response[0]['date'])}.
        The Air Quality Index on {str(data_analyzer_response[0]['date'])} will be
        {str(data_analyzer_response[0]['aqi'])} and the temperature will be
        {str(round(data_analyzer_response[0]['temperature_2m_max'],2))}
        degrees celsius. There are
        {str(round(data_analyzer_response[0]['precipitation_hours'],0))}
        hours of rain forecasted.
    """
    return Response(content=html_content, media_type="text/html")
    '''
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
