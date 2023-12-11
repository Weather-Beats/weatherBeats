# import relevant libraries
import os
import ssl
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from flask import Flask
from pyngrok import ngrok, conf, installer

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import base64
from io import BytesIO

import requests

# Refer to envschema.txt for the environment variables
load_dotenv()


class SQLServer:
    '''
    
    Class to connect to the SQL Server database.

    '''
    def __init__(self, db_name='public'):
        self.username = os.getenv('DB_USERNAME')
        self.password = os.getenv('DB_PASSWORD')
        self.host = os.getenv('DB_HOST')
        self.db_name = db_name
        self.connect()

        # we get the image off the bat because matplotlib does not support multithreading
        # image stored in self.image attribute
        sql = """SELECT mood, COUNT(mood) AS mood_count
            FROM weatherBeats_songToMood
            GROUP BY mood
            ORDER BY mood_count DESC
            LIMIT 10
        """
        self.image = self.get_image(sql)

    # Connect to the database
    def connect(self):
        conn_string = 'mysql+pymysql://{user}:{password}@{host}/{db}?charset={encoding}'.format(
                        host = self.host,
                        user = self.username,
                        db = self.db_name,
                        password = self.password,
                        encoding = 'utf8mb4')

        self.engine = create_engine(conn_string)


    # Query the database
    def query(self, sql, img=False):

        with self.engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)

        # Return the dataframe if img is False
        if not img:
            result = df.to_dict(orient='records')
        else:
            result = df

        return result
        

    def get_image(self, sql):
        mood_count = self.query(sql, img=True)

        # Create a red background for the plot
        sns.set_style("darkgrid")
        plt.figure(figsize=(20, 12))

        # Top 10 mood_count plot -> top 10 retrieved from SQL query
        ax = sns.barplot(data=mood_count, x='mood_count', y='mood', color='#1EB2F7')

        # Label the x and y axes
        ax.set_ylabel("Count", fontsize=19)
        ax.set_xlabel("Number of Songs", fontsize=19)
        ax.tick_params(axis='both', labelsize=16)

        # Save the plot as an image
        buf = BytesIO()
        plt.savefig(buf, format="png")
        data = base64.b64encode(buf.getbuffer()).decode("ascii")

        # Response - as dictionary
        results = {"image": data}

        return results

    def get_location_image(self, lat, long):
        url = f"""
            https://maps.googleapis.com/maps/api/staticmap?center={lat},{long}&zoom=4&size=700x700&maptype=roadmap&markers=color:red%7Clabel:C%7C{lat},{long}&key={os.getenv("GOOGLE_MAPS_API_KEY")}
            """
        
        # Get the image from the url
        response = requests.get(url)
        image = response.content

        # Encode the image
        encoded_image = base64.b64encode(image).decode("ascii")

        # Response - as dictionary
        results = {"image": encoded_image}

        return results


# Flask setup
class FlaskSetup:
    '''
    Class to setup Flask app.
    '''
    def __init__(self):
        self.port = os.getenv('FLASK_PORT')

        # Handle ngrok installation errors
        pyngrok_config = conf.get_default()
        if not os.path.exists(pyngrok_config.ngrok_path):
            myssl = ssl.create_default_context();
            myssl.check_hostname=False
            myssl.verify_mode=ssl.CERT_NONE
            installer.install_ngrok(pyngrok_config.ngrok_path, context=myssl)

        # Get the ngrok auth token from dotenv file
        self.ngrok_auth_token = os.getenv('NGROK_AUTH_TOKEN')
        ngrok.set_auth_token(self.ngrok_auth_token)

        self.curr_directory = os.path.dirname(os.path.abspath(__file__))
        self.directory = os.path.join(self.curr_directory, 'templates')

    # Connect to ngrok
    def connect(self):
        app = Flask(__name__, template_folder=self.directory)
        public_url = ngrok.connect(self.port).public_url
        app.config["BASE_URL"] = public_url
        
        # Make it more visible
        print("\n\n")
        print("-"*90)
        print(f" NGROK TUNNEL:  '{public_url}'-> 'http://127.0.0.1:{self.port}'")
        print("-"*90)
        print("\n\n")

        return app

class WeatherAPI:
    def __init__(self):
        self.api_key = os.getenv('WEATHER_API_KEY')

class OpenAIAPI:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')


# Instantiate the classes
db = SQLServer()
flask_app = FlaskSetup()
app = flask_app.connect()
weather_app = WeatherAPI()
openai_app = OpenAIAPI()