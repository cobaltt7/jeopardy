from enum import Enum, IntEnum
from typing import Literal

CATEGORIES = 2
VALUES = (200, 400, 600, 800, 1000)
TOTAL_QUESTIONS = len(VALUES) * CATEGORIES

ROUNDS = ("Jeopardy!", "Double Jeopardy!", "Final Jeopardy!")
RoundName = Literal["Jeopardy!", "Double Jeopardy!", "Final Jeopardy!"]


class Round(IntEnum):
    Lobby = -1
    Jeopardy = 0
    DoubleJeopardy = 1
    FinalJeopardy = 2
    End = 3


class Answer(Enum):
    No = "0"
    Loss = "1"
    Gain = "2"
