from enum import Enum
from typing import Literal

VALUES = (200, 400, 600, 800, 1000)
CATEGORIES = 2 # 6
TOTAL_QUESTIONS = len(VALUES) * CATEGORIES

Round = Literal[0, 1, 2]
ROUNDS = ("Jeopardy!", "Double Jeopardy!", "Final Jeopardy!")


class Answer(Enum):
    No = "0"
    Loss = "1"
    Gain = "2"
