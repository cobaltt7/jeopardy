from enum import StrEnum, auto


class Errors(StrEnum):
    no_room = auto()
    invalid_room = auto()
    no_player = auto()
    invalid_player = auto()
    duplicate_player = auto()
