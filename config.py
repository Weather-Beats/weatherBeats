
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from flask import Flask
from pyngrok import ngrok

import pandas as pd

# Refer to envschema.txt for the environment variables
load_dotenv()


class SQLServer:
    '''
    
    Class to connect to the SQL Server database.

    '''

    def __init__(self, db_name='public'):
        self.username = os.getenv('DB_USERNAME')
        self.password = os.getenv('DB_PASSWORD')
        self.host = 'db.ipeirotis.org'
        self.db_name = db_name
        self.connect()

    def connect(self):
        conn_string = 'mysql+pymysql://{user}:{password}@{host}/{db}?charset={encoding}'.format(
                        host = self.host,
                        user = self.username,
                        db = self.db_name,
                        password = self.password,
                        encoding = 'utf8mb4')

        self.engine = create_engine(conn_string)


    def query(self, sql):

        with self.engine.connect() as conn:
            df = pd.read_sql(sql, conn)

        df.to_dict(orient='records')

        return df




class FlaskSetup:
    '''
    
    Class to setup Flask app.

    '''
    def __init__(self):
        self.port = os.getenv('FLASK_PORT')
        self.ngrok_auth_token = os.getenv('NGROK_AUTH_TOKEN')
        ngrok.set_auth_token(self.ngrok_auth_token)

        self.curr_directory = os.path.dirname(os.path.abspath(__file__))
        self.directory = os.path.join(self.curr_directory, 'templates')

    def connect(self):
        app = Flask(__name__, template_folder=self.directory)
        public_url = ngrok.connect(self.port).public_url
        app.config["BASE_URL"] = public_url
        print(f" * ngrok tunnel '{public_url}' -> 'http://127.0.0.1:{self.port}'")

        return app
