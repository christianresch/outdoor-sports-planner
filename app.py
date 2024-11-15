from typing import Union

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from starlette.responses import Response

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
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Outdoor sports planner</title>
        <style>
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
                font-size: 16px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }}
            th {{
                background-color: #f4f4f4;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            tr:hover {{
                background-color: #f1f1f1;
            }}
        </style>
    </head>
    <body>
        <h1> Your outdoor sports prediction for {user_input}</h1>
        You are in <b>{user_input}</b>. Today is 15 November 2024. The best day for outdoor sport in the next couple days is <b>Sunday, 17 November 2024</b>. 
        <h1>PM<sub>2.5</sub> Data (Mock data taken from Bogota on 15 Nov)</h1>
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Average (µg/m³)</th>
                    <th>Max (µg/m³)</th>
                    <th>Min (µg/m³)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>2024-11-15</td>
                    <td>63</td>
                    <td>94</td>
                    <td>35</td>
                </tr>
                <tr>
                    <td>2024-11-16</td>
                    <td>72</td>
                    <td>104</td>
                    <td>46</td>
                </tr>
                <tr>
                    <td><b>2024-11-17</b></td>
                    <td><b>55</b></td>
                    <td><b>81</b></td>
                    <td><b>18</b></td>
                </tr>
                <tr>
                    <td>2024-11-18</td>
                    <td>96</td>
                    <td>152</td>
                    <td>36</td>
                </tr>
                <tr>
                    <td>2024-11-19</td>
                    <td>94</td>
                    <td>149</td>
                    <td>50</td>
                </tr>
            </tbody>
        </table>
        Note: PM<sub>2.5</sub> measures particle pollution of material with less than 2.5 micrometers (µm) in diameter, e.g. combustion particles. They are generally seen as the most hazardous particle pollution.<br>
        Source: OAB - El Observatorio Ambiental de Bogota via <a href=aqcin.org>AQCIN</a>
    </body>
    </html>
    """
    return Response(content=html_content, media_type='text/html')