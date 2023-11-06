# weatherBeats
<!-- Write me a description of the project -->
## Description
This is a web application that allows users to search for a city and get the current weather and a Spotify playlist based on the weather.

## Pipeline
<!-- Write me a description of the pipeline -->
The user enters a city name and clicks the search button. The city name is sent to the server and the server makes a request to the OpenWeatherMap API to get the current weather. The server then makes a request to the Spotify API to get a playlist based on the weather. The server then sends the weather and playlist to the client. The client then displays the weather and playlist to the user.

However, the current pipeline uses a database with all the required data instead of making requests to the APIs. The server makes a request to the database to get the weather and playlist. The server then sends the weather and playlist to the client. The client then displays the weather and playlist to the user.

## Motivation
We created this project to help users find music based on the weather. We wanted to create a fun and interactive way for users to find music that fits their mood.

## Table of Contents
* [Installation](#installation)
* [Usage](#usage)
* [Credits](#credits)

## Installation
<!-- How to install the project -->
To install this project, clone the repository.<br>

Create a virtual environment:
```
python3 -m venv venv
```
Activate the virtual environment:
```
source venv/bin/activate
```
Install the requirements:
```
pip install -r requirements.txt
```

Create a .env file in the root directory and add the following:
```javascript
DB_USERNAME='yourusername'
DB_PASSWORD='yourpassword'
DB_HOST='yourDBhost'

FLASK_PORT=5000
NGROK_AUTH_TOKEN='yourtoken'
```

Run the following script in terminal:
```
python main.py
```
This will start the server on port `you specified`. Open a browser and go to localhost:5000 to use the application

## Usage
<!-- How to use the project -->
To use this project, type in a city name and click the search button. The current weather will be displayed along with a playlist based on the weather.

## Credits
<!-- List your collaborators, if any, with links to their GitHub profiles. Links to websites or resources. -->
This project was created by [Laura Stocksdale](https://www.github.com/laurastocksdale), [Samyam Lamichhane](https://www.github.com/declansam), [Sarthak Prasad Malla](https://www.github.com/Sarthak-Malla), and [Tengis](https://www.github.com/Tengis0618).