from flask import request, session
from flask_socketio import send

from .app import app, socket
from .errors import Error
from .server import server
from .websocket import handle_disconnect, handle_message


@app.route("/", methods=["GET", "POST"])
def index():
    return server(request, session)


@socket.on("message")
def on_message(*message):
    response = (
        handle_message(message[0], request.sid)  # type: ignore
        if "action" in message[0]
        else Error.no_action
    )
    send(
        {"action": "ack", "sent_action": message[0]["action"]}
        if response is None
        else {
            "action": "error",
            "failed_action": message[0]["action"],
            "error": response,
        }
    )


@socket.on("disconnect")
def on_disconnect():
    handle_disconnect(request.sid)  # type: ignore


if __name__ == "__main__":
    socket.run(app, debug=True, host="0.0.0.0", port=81)
