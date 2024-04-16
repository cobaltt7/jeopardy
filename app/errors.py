from enum import StrEnum, auto


class Error(StrEnum):
    no_room = auto()
    invalid_room = auto()
    no_auth = auto()
    invalid_auth = auto()
    no_action = auto()
    invalid_action = auto()
