from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from starlette.responses import Response
from components.data_collectors.src.weather_data_collector import WeatherDataCollector
from components.data_gateways.src.weather_data_gateway import WeatherDataGateway
from components.data_collectors.src.coordinates_collector import CoordinatesCollector
import os

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def main():
    return '''
    
    <h1> Outdoor sports planner</h1>
    <h2> Get the best outdoor sport days based on air quality</h2>
    
    Enter your location here: <br>
    <br>
     <form action="/dummy_air_quality_data" method="POST">
         <input name="user_input">
         <input type="submit" value="Submit!">
     </form>
    (Note: This is just a dummy website so far and won't actually give you real information)<br>
    
     '''
@app.post("/dummy_air_quality_data")
async def dummy_air_quality_data(user_input: str = Form(...)):
    user_input = user_input.capitalize()
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    </head>
    <body>
        <h1> Your outdoor sports prediction for {user_input}</h1>
        You are in <b>{user_input}</b>. [PLACEHOLDER FOR CONTENT]</h1>
    """
    return Response(content=html_content, media_type='text/html')

if __name__ == "__main__":
    weather_collector = WeatherDataCollector()
    coordinates_collector = CoordinatesCollector()

    gateway = WeatherDataGateway(db_path="sqlite:///test_weather.db")

    if not os.path.exists("weather.db"):
        gateway.create()

    city = "Bogota"

    latitude, longitude = coordinates_collector.get_coordinates(city)

    temperature = weather_collector.get_weather_data(latitude, longitude)

    gateway.insert_weather_data(city, latitude, longitude, temperature)

    inserted_record = gateway.get_weather_data_by_city(city)[0]

    print(inserted_record.city)
    print(inserted_record.latitude)
    print(inserted_record.longitude)
    print(inserted_record.temperature)
    print(inserted_record.recorded_at)


