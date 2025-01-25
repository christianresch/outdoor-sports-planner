from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from starlette.responses import Response
from loguru import logger
import httpx
import os

app = FastAPI()

# TODO Adapt this!
DATA_ANALYZER_API_URL = "http://localhost:8003/analyze"

@app.get("/", response_class=HTMLResponse)
async def main():
    return '''
    
    <h1> Outdoor sports planner</h1>
    <h2> Get the best outdoor sport days based on air quality and weather forecast</h2>
    
    Enter your location here: <br>
    <br>
     <form action="/best_outdoor_sports_day" method="POST">
         <input name="user_input">
         <input type="submit" value="Submit!">
     </form>
    
     '''
@app.post("/best_outdoor_sports_day")
async def best_outdoor_sports_day(user_input: str = Form(...)):
    user_input = user_input.capitalize()

    logger.info(f"Request received with city: {user_input}, latitude: to be added and longitude: to be added")

    params = {}
    params["city"] = user_input

    async with httpx.AsyncClient() as client:
        logger.info(f"Fetching best sports day with params: {params}")
        data_analyzer_response = await client.post(DATA_ANALYZER_API_URL, json=params)
        if data_analyzer_response.status_code != 200:
            raise HTTPException(status_code=data_analyzer_response.status_code, detail="Error fetching best sports day.")
        logger.info(f"Best sports day received with {data_analyzer_response.status_code} status code")
        data_analyzer_response = data_analyzer_response.json()

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    </head>
    <body>
        <h1> Your outdoor sports prediction for {user_input}</h1>
        You are in <b>{user_input}</b>. Your best outdoor sports day in the coming days is {str(data_analyzer_response[0]['date'])}.
        The Air Quality Index on  {str(data_analyzer_response[0]['date'])} will be {str(data_analyzer_response[0]['aqi'])} 
        and the temperature will be  {str(round(data_analyzer_response[0]['temperature_2m_max'],2))} degrees celsius. 
        There are {str(round(data_analyzer_response[0]['precipitation_hours'],0))} hours of rain forecasted.
    """
    return Response(content=html_content, media_type='text/html')

#TODO Add /health-check endpoint, see Production Monitoring Video and a metrics endpoint (Prometheus in the example)
