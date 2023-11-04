

from config import db, flask_app, app
from flask import render_template, request, jsonify

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/song.html", methods=["GET"])
def song():
    return render_template("song.html")


@app.route("/moodFromWeatherAPI", methods=["GET"])
def moodFromWeatherAPI():
    
    # SQL Variables
    table_name = 'weatherBeats_weather_w_location'

    
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

    query_resp = db.query(sql)
    print("Mood:\n", query_resp, "\n")

    result = {
        'location': param,
        'mood': query_resp
    }

    return jsonify(result)

















app.run(use_reloader=False, port=flask_app.port)



