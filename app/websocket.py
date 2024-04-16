from .app import socket
from .errors import Error
from .rooms import rooms
from .users import disconnected


def handle_message(message, sid: str) -> Error | None:
    print(message, sid)
    if "room" not in message:
        return Error.no_room
    if message["room"] not in rooms:
        return Error.invalid_room
    room = rooms[message["room"]]

    if "auth" not in message:
        return Error.no_auth

    match message["action"]:
        case "join":
            if message["auth"] == room.host.auth_key:
                if room.host.sid == sid:
                    return
                if room.host.sid:
                    socket.send({"action": "disconnect"}, to=room.host.sid)
                room.host.sid = sid
                return

            player = next(
                filter(lambda player: player.auth_key == message["auth"], room.players),
                None,
            )
            if not player:
                return Error.invalid_auth

            print(player.auth_key, player.sid, sid, player.name)
            if player.sid == sid:
                return
            if player.sid:
                player.emit({"action": "disconnect"})
            player.sid = sid

        case "ready":
            if message["auth"] != room.host.auth_key:
                return Error.invalid_auth
            room.emit({"action": "ready"})

        case _:
            return Error.invalid_action


def handle_disconnect(sid: str):
    disconnected.add(sid)
