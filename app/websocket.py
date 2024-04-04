from .app import socket
from .errors import Error
from .rooms import rooms


def handle_message(message, sid) -> Error | None:
    match message["action"]:
        case "join":
            if "room" not in message:
                return Error.no_room
            if message["room"] not in rooms:
                return Error.invalid_room
            room = rooms[message["room"]]

            if "player" not in message:
                return Error.no_player

            if message["player"] == room.host:
                if room.host_sid and room.host_sid != sid:
                    socket.send({"action": "disconnect"}, to=room.host_sid)
                room.host_sid = sid
                return

            player = next(
                filter(
                    lambda player: player.auth_key == message["player"], room.players
                ),
                None,
            )
            if not player:
                return Error.invalid_player

            if player.sid != sid:
                player.send({"action": "disconnect"})
            player.sid = sid
