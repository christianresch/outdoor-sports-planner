from typing import Union

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from starlette.responses import Response

app = FastAPI()

# TODO Add the needed echo functionalities from https://www.coursera.org/learn/software-architecture-for-big-data-applications/supplement/c8fpb/setting-up-a-web-application

# TODO Deploy this to Heroku. Note that you can export the requirements from Poetry via poetry export -f requirements.txt --output requirements.txt and need to adapt the Procfile to 'web: uvicorn main:app --host 0.0.0.0 --port ${PORT:-5000}'

@app.get("/", response_class=HTMLResponse)
async def main():
    return '''
    
    Enter your text here:
    
     <form action="/echo_user_input" method="POST">
         <input name="user_input">
         <input type="submit" value="Submit!">
     </form>
     '''

@app.post("/echo_user_input")
async def echo_input(user_input: str = Form(...)):
    return Response(content="You entered: " + user_input)