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
        case "buzz":
            if message["auth"] == room.host.auth_key:
                room.emit({"action": "buzz", "player": None})
                return
            player = next(
                filter(
                    lambda player: player.auth_key == message["auth"], room.all_players
                ),
                None,
            )
            if not player:
                return Error.invalid_auth
            room.emit({"action": "buzz", "player": player.name})

        case "join":
            player = next(
                filter(
                    lambda player: player.auth_key == message["auth"],
                    [*room.all_players, room.host],
                ),
                None,
            )
            if not player:
                return Error.invalid_auth

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
