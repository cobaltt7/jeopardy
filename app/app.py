from os import path

from flask import Flask
from flask_socketio import SocketIO

root_path = path.join(path.dirname(path.abspath(__file__)), "../")
app = Flask(__name__, root_path=root_path)
app.secret_key = "cookie_signing_secret"
app.config["SECRET_KEY"] = "secret!"
socket = SocketIO(app)
