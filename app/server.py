from flask import Request, redirect, render_template
from flask.sessions import SessionMixin

from .rooms import Room, rooms
from .users import Player
from .util import Answer, Round


def server(request: Request, session: SessionMixin):
    action = request.method == "POST" and request.form.get("action", False)
    opened_question = False

    if action == "create":
        room = Room()
        session["auth_key"] = room.host.auth_key
        session["room"] = room.id
    elif action == "join":
        room_id = request.form.get("room", "").upper()
        if room_id == "" or room_id not in rooms:
            return render_template("index.html")
        room = rooms[room_id]

        name = request.form.get("name", "").strip().upper()
        if not name or next(
            (True for player in room.all_players if player.name == name), False
        ):
            return render_template("index.html")

        player = Player(name)
        room.emit({"action": "join", "player": player.name})
        room.all_players.append(player)
        session["auth_key"] = player.auth_key
        session["room"] = room.id
    elif "auth_key" not in session:
        return render_template("index.html")
    elif "room" not in session or session["room"] not in rooms:
        return render_template("index.html")
    else:
        room = rooms[session["room"]]
        if (
            not room.current_question
            and session["auth_key"] == room.current_player.auth_key
        ):
            room.current_question = request.args.get("question", type=int)
            opened_question = room.current_question is not None

    if action == "close" and session["auth_key"] == room.host.auth_key:
        del session["room"]
        del rooms[room.id]
        room.emit({"action": "close"})
        return render_template("index.html")

    if room.round_index is Round.Lobby:
        if action != "start" or session["auth_key"] != room.host.auth_key:
            return render_template("lobby.html", room=room)
        room.refresh_questions()
        room.emit({"action": "reload", "reason": "start"}, exclude=session["auth_key"])
    elif action == "answer":
        if not room.current_question or session["auth_key"] != room.host.auth_key:
            return redirect(request.path)
        answers = map(
            lambda player: (
                player[1],
                request.form.get(f"guess-{player[0]}", Answer.No, type=Answer),
            ),
            enumerate(room.players),
        )
        value = room.question_index[room.current_question].value or 0
        for player, answer in answers:
            if answer is Answer.Gain:
                player.money += value
                room.current_player = player
            elif answer is Answer.Loss:
                player.money -= value
        room.done_questions.append(room.current_question)
        room.current_question = None
        room.refresh_questions()
        room.emit({"action": "reload", "reason": "answer"}, exclude=session["auth_key"])
    elif action == "handle-wagers":
        if not room.current_question or session["auth_key"] != room.host.auth_key:
            return redirect(request.path)
        room.handle_wagers(request.form)
        room.done_questions.append(room.current_question)
        room.current_question = None
        room.refresh_questions()
        room.emit({"action": "reload", "reason": "answer"}, exclude=session["auth_key"])
    elif room.current_question:
        if room.current_question in room.available_questions:
            if opened_question:
                room.emit(
                    {"action": "reload", "reason": "question"},
                    exclude=session["auth_key"],
                )
            return render_template(
                "question.html",
                question=room.question_index[room.current_question],
                room=room,
                last=len(room.available_questions) == 1,
            )
        room.current_question = None

    if room.round_index is Round.End:
        del session["room"]
        return render_template("end.html", room=room)

    if len(room.available_questions) == 1:
        room.current_question = room.available_questions[0]
        return render_template(
            "question.html",
            question=room.question_index[room.current_question],
            room=room,
            last=True,
        )

    return render_template("questions.html", room=room)
