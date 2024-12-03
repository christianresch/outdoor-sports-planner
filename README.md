# Outdoor sports planner

This is the repo for the outdoor sports planner app, developed as the capstone project for the CU Boulder Online MSCS class in software architecture for big data.

## Introduction

Hi! Welcome!

This is the version of my outdoor sports planner for the data collection assignment. 
As you can see, I have worked on this assignment as part of building the overall application. This means a couple of things:

1. The structure is more complicated than necessary for this assignment. 
I already created collectors and data gateways to manage API calls and database interactions.
2. You will find some TODOs that I wrote myself for later when I fully build out the application (e.g. I have not yet solved how to handle time zones well).

This version of the README should help you to get the current data collectors and gateways running so you can check that they work as intended. Otherwise, be welcome to have a look and leave some feedback! 

I am looking forward to it,
Christian

## Where to find what

For this assignment, the relevant files are the data collector ``weather_data_collector.py`` in ``components/data_collectors/src/`` 
and the data gateway ``weather_data_gateway.py`` in ``components/data_dateways/src/``. 

So you can test it, I combined all necessary steps into one example in ``app.py`` in ``applications/web_server/src/``

## Set up

This project is written in Python 3.10, therefore if you do not have this version of Python installed, you need to run 
````commandline
pyenv install 3.10.0
````

I use Poetry to manage my dependencies. 
Therefore, if you do not yet have installed Poetry, you would need to run 
```` 
brew update
brew install poetry 
```` 
if you use macOS or Linux have Homebrew installed, or check [their documentation](https://python-poetry.org/docs/), including for Windows. 
(I cannot confirm what works for Windows so did not want to give you any wrong guide).

Once you have Poetry installed, you need to run
````commandline
poetry install
````
to install all dependencies and then
````commandline
poetry shell
````
to start the virtual environment.

Alternatively, I also exported all dependencies into a requirement.txt that you could use to install dependencies using pip:
````commandline
pip install -r requirements.txt
````
Please note that I did not test this approach.

## Running the collector and data gateway

To test run the data collector and data gateway, you might need to make sure that Python correctly finds all modules.

Therefore, run
````commandline
export PYTHONPATH=$(pwd)
````
on macOS/Linux or
````commandline
set PYTHONPATH=%cd%
````
on Windows before running
````commandline
poetry run python applications/web_server/src/app.py 
````

If you aren't using Poetry, you would need to activate the virtual environment manually and then run
````commandline
python applications/web_server/src/app.py 
````

You will see that a ``test_weather.db`` gets created. 
To reset, just delete the file, and it will be created again on the next run. 
If you do not delete it and run the command again, more records will be added to the database.
In your command line, you will see the record for Bogotá that you just queried and then stored to the database.