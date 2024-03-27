from os import path

from flask import Flask, redirect, render_template, request, session
from flask_socketio import SocketIO, send

from .util import Answer
from .rooms import Room, rooms
from .websocket import handle_message

root_path = path.join(path.dirname(path.abspath(__file__)), "../")
app = Flask(__name__, root_path=root_path)
app.secret_key = "cookie_signing_secret"
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)


@app.route("/", methods=["GET", "POST"])
def index():
    action = request.method == "POST" and request.form.get("action", "create")

    if action == "create":
        room = Room(request.form)
        question_index = None
        session["room"] = room.id
    elif "room" in session and session["room"] in rooms:
        room = rooms[session["room"]]
        question_index = request.args.get("question", type=int)
    else:
        return render_template("index.html")

    if action == "answer":
        if not room.done_questions:
            return redirect(request.path)
        guesses = map(
            lambda player: (
                player[1],
                request.form.get(f"guess-{player[0]}", Answer.No, type=Answer),
            ),
            enumerate(room.players),
        )
        for player, guess in guesses:
            player.answer_question(room.done_questions[-1], guess)
    elif action == "handle-wagers":
        if not room.done_questions:
            return redirect(request.path)
        room.handle_wagers(request.form)
    elif question_index is not None:
        question_data = next(
            filter(
                lambda question: question.original_index == question_index,
                room.available_questions,
            ),
            None,
        )
        if question_data is not None:
            room.done_questions.append(question_index)
            return render_template(
                "question.html",
                question=question_data,
                room=room,
                last=False,
            )

    room.refresh_questions()
    question_count = len(room.available_questions)
    if question_count == 1:
        question_data = room.available_questions[0]
        room.done_questions.append(question_data.original_index)
        return render_template(
            "question.html",
            question=question_data,
            room=room,
            last=True,
        )
    if question_count == 0:
        del session["room"]
        room.sort_players()
        return render_template("end.html", room=room)

    return render_template(
        "questions.html",
        room=room,
    )


@socketio.on("message")
def my_event(*message):
    response = handle_message(message[0])
    if response:
        send(response)


if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=81)
