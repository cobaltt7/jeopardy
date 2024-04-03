from flask import redirect, render_template, request, session
from flask_socketio import send

from .app import app, socket
from .util import Answer, Round
from .rooms import Player, Room, rooms
from .websocket import handle_message


@app.route("/", methods=["GET", "POST"])
def index():
    action = request.method == "POST" and request.form.get("action", False)

    if action == "create":
        room = Room(request.form)
        session["host"] = room.host
        session["player"] = None
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
        session["host"] = False
        session["player"] = player.id
        session["room"] = room.id
    elif "room" not in session or session["room"] not in rooms:
        return render_template("index.html")
    else:
        room = rooms[session["room"]]
        question_index = request.args.get("question", type=int)

    if action == "close" and session["host"] == room.host:
        del session["room"]
        room.send({"action": "close"})
        return render_template("index.html")

    if room.round_index == Round.Lobby:
        if action != "start" or session["host"] != room.host:
            # room.send({"action": "start"})
            return render_template(
                "lobby.html",
                room=room,
                player=session["player"],
                host=bool(session["host"]),
            )
    elif action == "answer":
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

    return render_template("questions.html", room=room)


@socket.on("message")
def my_event(*message):
    if "action" not in message[0]:
        return
    response = handle_message(message[0], request.sid)
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
