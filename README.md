# Outdoor sports planner

This is the repo for the outdoor sports planner app, developed as the capstone project for the CU Boulder Online MSCS class in software architecture for big data.

## Introduction

Hi! Welcome!

This is my outdoor sports planner for final assignment of CSCA 5028 of the CU Boulder Online MSCS class in software architecture for big data.

This repo includes all parts of the outdoor sports planner app that uses weather and AQI information to predict the best day to do outdoor sports in the user's location.

This version of the README should help you to get a local version of the application running so you can check that they work as intended. Otherwise, be welcome to have a look and leave some feedback!

I am looking forward to it,
Christian

## Where to find what

The app follows the discussed general outline. That means, there is

1. An ``applications`` folder where you can find all four web servers that make up the applications. Those are the ``web_server`` for the user interface,
the ``data_analyzer_server`` which predicts the best days and the two data collector servers ``aqi_data_collector_server`` and ``weather_data_collector_server``
which interact with the APIs to retrieve data and store it for later analysis.
2. A ``components`` folder which contains all functionalities in separate classes which the servers use to implement their functionalities.
3. Integration and unit tests which are located together with the respective components or servers that they are testing.

## Project rubric

To make it easier for you to check whether everything is there, here an overview where you find the parts of the project rubric:

**C Level Work**

* Web application basic form, reporting: In ``applications/web_server``
* Data collection: In ``applications/data_collector_server`` and the used components
* Data analyzer  In ``applications/data_analyzer_server`` and the used components
* Unit tests: In all ``test/`` folders. For an overview, run ``pytest``
* Data persistence any data store: Used in ``applications/data_collector_server``. Data gateways are found in ``components/data_gateways``
* Rest collaboration internal or API endpoint: Internal API end points in all servers. External API endpoint used in ``applications/data_collector_server``.
* Product environment: See Docker files

**B Level Work**

* Integration tests: In the test of the servers and most components, e.g. in ``applications/data_analyzer_server/test/data_analyzer_server_test.py``
* Using mock objects, fakes, or spys: In tests of most components, e.g. in ``components/data_analyzers/test/weather_aqi_analyzer_test.py``
* Continuous integration: See yaml files in ``.github/workflows``
* Production monitoring instrumenting: See ``applications/web_server/src/app.py``

**A Level Work**

* Event collaboration messaging: See RabbitMQ implementation between the web server in ``applications/web_server``
and the data analyzer server in ``applications/data_analyzer_server`` as well as in the ``docker-compose.yaml``
* Continuous delivery: See yaml files in ``.github/workflows``

## Requirements

**AQI API Access**

This app relies on the API from https://aqicn.org for its air quality data. The API is free but requires registration and a token for access which you can get at https://aqicn.org/data-platform/token/.

This token needs to be stored in a .env files in the root directory as ``AQICN_TOKEN``.

**Other requirements**

This project is written in Python 3.10, therefore if you do not have this version of Python installed, you need to run
````commandline
pyenv install 3.10.0
````

I used Poetry for the dependency management and Docker and Docker Compose for deployment. You would therefore need to make sure that Poetry, Docker and Docker compose are installed on your machine.

If you do not yet have installed Poetry, you would need to run
````
brew update
brew install poetry
````
if you use macOS or Linux have Homebrew installed, or check [their documentation](https://python-poetry.org/docs/), including for Windows.
(I cannot confirm what works for Windows so did not want to give you any wrong guide).

For Docker, you can find installation guides here:
* Docker https://docs.docker.com/desktop/
* https://docs.docker.com/compose/install/

## Set up

Once you have Poetry installed, you need to run
````commandline
poetry install
````
to install all dependencies and then
````commandline
poetry shell
````
to start the Poetry environment.

Alternatively, I also exported all dependencies into a requirement.txt that you could use to install dependencies using pip:
````commandline
pip install -r requirements.txt
````
Please note that I did not test this approach.

## Running the application

Once all the requirements are installed, you can simply run

````commandline
docker compose up
````

if you installed Docker Compose together with Docker or

````commandline
docker-compose up
````

for the standalone version of Docker Compose.

This will run all servers in different Docker containers and sets up their API interactions.

You can then access the application at ``localhost:8000/`` or ``127.0.0.1:8000/`` which will lead you to the web page
from which you can get a prediction for the best outdoor sports day based on the weather and air quality data of the given location.

(For some locations, either air quality or weather data is not available. I live in Bogota and can confirm that this works reliably.)
