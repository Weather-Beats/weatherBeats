

from config import SQLServer, FlaskSetup

db = SQLServer()
# sql =   f'''
#             SELECT * FROM weatherBeats_spotify
#         '''
# print(db.query(sql))

flask_app = FlaskSetup()
app = flask_app.connect()

@app.route("/home")
def hello():
    return "Hello Panos!"

app.run(use_reloader=False, port=flask_app.port)



