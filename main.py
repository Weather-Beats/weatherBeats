
# Importing custom modules and libraries
from config import db, flask_app, app, weather_app, openai_app
from utils.defaults import DEFAULT_MOOD, DB_MOOD_FROM_WEATHER, DB_SONGS_FROM_MOOD, DB_SPOTIFY_LYRICS, DB_LOCATIONS, DB_SONGS_FROM_MOOD_ML, DB_SONGS_15k
from flask import render_template, request, jsonify
import requests
from openai import OpenAI
import json
import folium

# renders the homepage for the website
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

# renders the moods page for the website
@app.route("/moods.html", methods=["GET"])
def moods():
    return render_template("moods.html")

# render the list of songs after the user has selected a location and the mood is extracted
@app.route("/song.html", methods=["GET"])
def song():
    return render_template("song.html")

# renders the 'visualizations' page for the website
@app.route("/dataviz.html", methods=["GET"])
def visualizations():
    return render_template("visualizations.html")

# plot the number of songs with a particular mood
@app.route('/moodVizAPI',  methods=['GET'])
def moodViz():
    # the image is pre-generated and stored in the config.py file
    results = db.image

    # JSON-ified response
    return jsonify(results)

# location map
@app.route('/locationVizAPI',  methods=['GET'])
def locationViz():
    lat = str(request.args.get('lat'))
    long = str(request.args.get('long'))

    # the image is pre-generated and stored in the config.py file
    results = db.get_location_image(lat, long)

    # JSON-ified response
    return jsonify(results)


# Route to get the mood of the location provided by the user
@app.route("/moodFromWeatherAPI", methods=["GET"])
def moodFromWeatherAPI():
    """
    Returns the mood of the location provided by the user
    """
    
    # SQL Variables
    table_name = DB_MOOD_FROM_WEATHER

    # Get location from query
    param = str(request.args.get('location'))
    print("\nCity: ", param)

    # Check if location was provided
    if (len(param) == 0):
        return jsonify({'error': 'No location provided'})
    
    # Get weather data from API
    sql = f'''
        
            SELECT mood FROM {table_name}
            WHERE cityname = "{param}"

        '''

    # Query the database
    query_resp = db.query(sql)
    print("Mood:\n", query_resp, "\n")

    # get the mood from the query response
    query_resp = query_resp[0]['mood']
    moods = query_resp.split(',')
    mood_list = [mood.strip() for mood in moods]

    # JSON-ified response
    result = {
        'location': param,
        'mood': mood_list
    }

    # Logging
    print("Result:\n", result, "\n")

    return jsonify(result)


# Route to get the songs from the mood retreived from 'location name'
@app.route("/songsFromMoodAPI", methods=["GET"])
def songsFromMood():
    """
    Gets the list of a moods and returns a list of songs
    """

    # SQL Variables
    table_name = DB_SONGS_FROM_MOOD
    lyrics_table_name = DB_SPOTIFY_LYRICS

    # Get checkbox value from query
    enableML = str(request.args.get('enableML'))
    print("Enable ML (songsFromMoodAPI) ", enableML)

    # Based on the checkbox value, we will use the ML table or the non-ML table
    if enableML == 'on':
        print("\nUsing ML table\n")
        table_name = DB_SONGS_FROM_MOOD_ML
        lyrics_table_name = DB_SONGS_15k

    # Get mood from query
    mood_list = request.args.get('moods').split(' ')
    if len(mood_list) > 1:
        param = tuple(mood_list)
    else:
        param = f"('{mood_list[0]}')"

    # Check if mood was provided
    if (len(param) == 0):
        return jsonify({'error': 'No mood provided'})
    
    # LOGGING
    print("\n\nTable Used; ", table_name)
    print("\n\nLyrics Table Used; ", lyrics_table_name)
    print("\n\n")

    # Get songs from API
    sql_nonml = f'''
            SELECT s.song_name, s.artist_name, s.genre, m.lyrics, m.url AS uri,
                    a.moods AS moods
            FROM {table_name} s
            JOIN
                (
                    SELECT
                        song_name,
                        artist_name,
                        GROUP_CONCAT(DISTINCT mood, '') AS moods
                    FROM
                        {table_name}
                    GROUP BY
                        song_name, artist_name
                ) a
            ON
                s.song_name = a.song_name AND s.artist_name = a.artist_name
            JOIN {lyrics_table_name} m ON s.song_name = m.song_name AND s.artist_name = m.artist_name
            WHERE s.mood IN {param}
            GROUP BY s.song_name, s.artist_name, s.genre, m.lyrics, uri
            '''

    sql_ml = f'''
            SELECT s.song_name, s.artist_name, s.genre, m.url AS uri,
                    a.moods AS moods
            FROM {table_name} s
            JOIN
                (
                    SELECT
                        song_name,
                        artist_name,
                        GROUP_CONCAT(DISTINCT mood, '') AS moods
                    FROM
                        {table_name}
                    GROUP BY
                        song_name, artist_name
                ) a
            ON
                s.song_name = a.song_name AND s.artist_name = a.artist_name
            JOIN {lyrics_table_name} m ON s.song_name = m.song_name AND s.artist_name = m.artist_name
            WHERE s.mood IN {param}
            GROUP BY s.song_name, s.artist_name, s.genre, uri
            '''   
    
    # If ML is enabled, use the ML query
    if enableML == 'on':
        print("\nUsing ML query\n")
        sql = sql_ml
    else:
        print("\nUsing non-ML query\n")
        sql = sql_nonml

    query_resp = db.query(sql)

    result = {
        'songs': query_resp
    }

    return jsonify(result)

# Route to get the lat and long of the location provided by the user
@app.route("/latlongFromWeatherAPI", methods=["GET"])
def latlongFromWeatherAPI():
    """
    Returns the lat and long of the location provided by the user
    """

    # SQL Variables
    # This table has cityname, and their latitude and longitude
    table_name = DB_LOCATIONS

    # Get location from query
    param = str(request.args.get('location'))
    enableML = str(request.args.get('enableML'))
    # print("\nCity: ", param)
    # print("\nEnable ML: ", enableML)

    # Check if location was provided
    if (len(param) == 0):
        return jsonify({'error': 'No location provided'})

    # Get weather data from API
    sql = f'''

            SELECT latitude, longtitude FROM {table_name}
            WHERE cityname = "{param}"

        '''

    # Query the database
    query_resp = db.query(sql)
    print("Data:\n", query_resp, "\n")

    result = get_weather_data(query_resp[0]["latitude"],
                              query_resp[0]["longtitude"],
                              weather_app.api_key)

    print("WeatherAPI Response (Result):\n", result, "\n")


    mood_result = weather_mood(result)

    # getting the name of the weather in the location
    weather_in_loc = result['weather'][0]['main']
    
    print("OPENAI Response (Mood Results):\n", mood_result, "\n")
  
    mood_list=[]
    try:
      for mood in mood_result["mood"]:
        mood_list.append(mood)
    except:
        mood_list.append(DEFAULT_MOOD)

    # JSON-ified response
    result = {
        'location': param,
        'lat': query_resp[0]["latitude"],
        'long': query_resp[0]["longtitude"],
        'mood': mood_list,
        'weather': weather_in_loc,
    }

    # Logging
    print("Final Result:\n", result, "\n")

    return jsonify(result)



def get_weather_data(latitude, longitude, api_key):
  # API endpoint URL
  api_url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}"

  # Make the API request
  response = requests.get(api_url)

  # Check if the request was successful (status code 200)
  if response.status_code == 200:
      # Parse the JSON data in the response
      weather_data = response.json()
      return weather_data
  else:
      # Print an error message if the request was not successful
      print(f"Error: Unable to fetch data. Status code: {response.status_code}")
      return None



def get_completion(prompt, model="gpt-3.5-turbo"):
  client = OpenAI(api_key=openai_app.api_key)
  response= client.chat.completions.create(
    model=model,
    messages=[
      {"role": "system", "content": "Given these weather informations, provide the associated mood. Assign 2-3 moods based on the moods list. Return an object with JSON format with name, description, temperature, humidity, clouds, wind_speed, humidity and mood as a field."},
      {"role": "user", "content": prompt}
    ],
  )

  return response.choices[0].message.content

def weather_mood(weather):
  '''
  This function takes as input a JSON object that has the same structure
  as an article coming back from NewsAPI and returns back the results
  from ChatGPT.
  '''

  name = weather['weather'][0]['main']
  description = weather['weather'][0]['description']
  temperature = weather['main']['temp']
  clouds = weather['clouds']
  winds = weather['wind']['speed']
  humidity = weather['main']['humidity']
  moods = [
    'Joyful',
    'Calm',
    'Energetic',
    'Contemplative',
    'Melancholic',
    'Startled',
    'Relaxed',
    'Content',
    'Mysterious',
    'Refreshed',
    'Invigorated',
    'Tranquil',
    'Exotic',
    'Sad',
    'Dispirited',
    'Anxious',
    'Gloomy',
    'Dreary',
    'Stormy',
    'Restless',
    'Depressed',
    'Tense',
    'Moody',
    'Sorrowful',
    'Worried',
]

# This list now consists of an equal amount of positive and negative/sad moods with a total of 26 elements.

  prompt = f'''Weather information: name: {name} --  description: {description} -- temp: {temperature} -- clouds: {clouds} -- wind: {winds} -- humidity{humidity} --moods: {moods}
  '''

  response = get_completion(prompt)
  data = json.loads(response)
  return data


@app.route("/map", methods=["GET"])
def interactivemap():

    table_name = DB_LOCATIONS
    
    param = str(request.args.get('location'))


    sql = f'''

            SELECT latitude, longtitude FROM {table_name}
            WHERE cityname = "{param}"

        '''

    # Query the database
    query_resp = db.query(sql)

    lat = float(query_resp[0]["latitude"])
    lon = float(query_resp[0]["longtitude"])

    print(query_resp)

    fmap = folium.Map(location=[lat, lon], zoom_start=12, tiles='OpenStreetMap')

    # Add marker for the location
    folium.CircleMarker(location=[lat, lon],
                        radius = 10.0, color='red', 
                        weight=0.8,
                        fill=True,
                        fill_opacity = 0.9,
                        fill_color = 'purple',
                       ).add_to(fmap)

    return fmap._repr_html_()



# ---------------------------------------------------------------

# Run the Flask app
app.run(use_reloader=False, port=flask_app.port)

# ---------------------------------------------------------------