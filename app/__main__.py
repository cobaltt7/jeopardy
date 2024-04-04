from flask import redirect, render_template, request, session
from flask_socketio import send

from .app import app, socket
from .questions import questions_df
from .rooms import Player, Room, rooms
from .util import Answer, Round
from .websocket import handle_message


@app.route("/", methods=["GET", "POST"])
def index():
    action = request.method == "POST" and request.form.get("action", False)

    if action == "create":
        room = Room(request.form)
        session["auth_key"] = room.host
        session["room"] = room.id
    elif action == "join":
        room_id = request.form.get("room", "").upper()
        if room_id == "" or room_id not in rooms:
            return render_template("index.html")
        room = rooms[room_id]

        name = request.form.get("name", "").strip().upper()
        if not name or next(
            (True for player in room.players if player.name == name), False
        ):
            return render_template("index.html")

        player = Player(name)
        room.send({"action": "join", "player": player.name})
        room.players.append(player)
        session["auth_key"] = player.auth_key
        session["room"] = room.id
    elif "auth_key" not in session:
        return render_template("index.html")
    elif "room" not in session or session["room"] not in rooms:
        return render_template("index.html")
    else:
        room = rooms[session["room"]]
        if not room.current_question:
            room.current_question = request.args.get("question", type=int)

    if action == "close" and session["auth_key"] == room.host:
        del session["room"]
        room.send({"action": "close"})
        return render_template("index.html")

    if room.round_index == Round.Lobby:
        if action != "start" or session["auth_key"] != room.host:
            return render_template("lobby.html")
        room.send({"action": "start"})
    elif action == "answer":
        if not room.current_question:
            return redirect(request.path)
        guesses = map(
            lambda player: (
                player[1],
                request.form.get(f"guess-{player[0]}", Answer.No, type=Answer),
            ),
            enumerate(room.players),
        )
        for player, guess in guesses:
            player.answer_question(room.current_question, guess)
        room.done_questions.append(room.current_question)
        room.current_question = None
    elif action == "handle-wagers":
        if not room.current_question:
            return redirect(request.path)
        room.handle_wagers(request.form)
        room.done_questions.append(room.current_question)
        room.current_question = None
    elif room.current_question:
        if room.current_question in room.available_questions:
            return render_template(
                "question.html",
                question=questions_df.iloc[room.current_question],
                room=room,
                last=False,
            )
        room.current_question = None

    room.refresh_questions()
    question_count = len(room.available_questions)
    if question_count == 1:
        room.current_question = room.available_questions[0]
        return render_template(
            "question.html",
            question=questions_df.iloc[room.current_question],
            room=room,
            last=True,
        )
    if question_count == 0:
        del session["room"]
        room.sort_players()
        return render_template("end.html", room=room)

    return render_template("questions.html", room=room)


@socket.on("message")
def my_event(*message):
    if "action" not in message[0]:
        return
    response = handle_message(message[0], request.sid)  # type: ignore
    if response is None:
        return
    send(
        {
            "action": "error",
            "failed_action": message[0]["action"],
            "error": response,
        }
    )


if __name__ == "__main__":
    socket.run(app, debug=True, host="0.0.0.0", port=81)
