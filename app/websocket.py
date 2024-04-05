from .app import socket
from .errors import Error
from .rooms import rooms


def handle_message(message, sid) -> Error | None:
    if "room" not in message:
        return Error.no_room
    if message["room"] not in rooms:
        return Error.invalid_room
    room = rooms[message["room"]]

    if "auth" not in message:
        return Error.no_auth

    match message["action"]:
        case "join":
            if message["auth"] == room.host:
                if room.host_sid == sid:
                    return
                if room.host_sid:
                    socket.send({"action": "disconnect"}, to=room.host_sid)
                room.host_sid = sid
                return

            player = next(
                filter(lambda player: player.auth_key == message["auth"], room.players),
                None,
            )
            if not player:
                return Error.invalid_auth

            if player.sid == sid:
                return
            player.send({"action": "disconnect"})
            player.sid = sid

        case "ready":
            if message["auth"] != room.host:
                return Error.invalid_auth
            room.send({"action": "ready"})
