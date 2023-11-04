
# Importing custom modules and libraries
from config import db, flask_app, app
from flask import render_template, request, jsonify

# renders the homepage for the website
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


# render the list of songs after the user has selected a location and the mood is extracted
@app.route("/song.html", methods=["GET"])
def song():
    return render_template("song.html")


# plot the number of songs with a particular mood
@app.route('/moodVizAPI',  methods=['GET'])
def moodViz():
    # the image is pre-generated and stored in the config.py file
    results = db.image

    # JSON-ified response
    return jsonify(results)


# Route to get the mood of the location provided by the user
@app.route("/moodFromWeatherAPI", methods=["GET"])
def moodFromWeatherAPI():
    """
    Returns the mood of the location provided by the user
    """
    
    # SQL Variables
    table_name = 'weatherBeats_weather_w_location'

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
    table_name = 'weatherBeats_songToMood'

    lyrics_table_name = 'weatherBeats_spotify_lyrics_url'

    mood_list = request.args.get('moods').split(' ')
    if len(mood_list) > 1:
        param = tuple(mood_list)
    else:
        param = f"('{mood_list[0]}')"

    # Check if mood was provided
    if (len(param) == 0):
        return jsonify({'error': 'No mood provided'})
    
    # Get songs from API
    sql = f'''
            SELECT s.song_name, s.artist_name, s.genre, m.lyrics, m.uri,
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
            GROUP BY s.song_name, s.artist_name, s.genre, m.lyrics, m.uri
            '''   
    
    query_resp = db.query(sql)

    result = {
        'songs': query_resp
    }

    return jsonify(result)



# ---------------------------------------------------------------

# Run the Flask app
app.run(use_reloader=False, port=flask_app.port)

# ---------------------------------------------------------------
