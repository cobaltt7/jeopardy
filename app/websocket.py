from .errors import Errors
from .rooms import Player, rooms


def handle_message(message):
    print(message)
    if "action" not in message:
        return
    match message["action"]:
        case "join":
            if "room" not in message:
                return {"action": message["action"], "error": Errors.no_room}
            if message["room"] not in rooms:
                return {"action": message["action"], "error": Errors.invalid_room}
            room = rooms[message["room"]]

            if "player" not in message:
                return {"action": message["action"], "error": Errors.no_player}
            name = message["player"].strip().upper()
            if name == "":
                return {"action": message["action"], "error": Errors.invalid_player}
            if next(
                (True for player in room.players if player.name == name), False
            ):
                return {"action": message["action"], "error": Errors.duplicate_player}

            room.players.append(Player(name))
