from datetime import date
from random import choices
from typing import Any, Literal

import pandas

from .util import VALUES, Round

questions_df = pandas.read_csv(
    "./questions_cleaned.csv",
    converters={"answer": lambda value: str(value)},
    parse_dates=["air_date"],
)


class Question:
    show: int
    air_date: date
    round: Round
    category: str
    value: int | None
    question: str
    answer: str
    original_index: int
    dd: bool

    def __init__(self, question):
        self.__dict__.update(question)


def pick_questions(category: pandas.DataFrame, round_index: Literal[0, 1], dd: Any):
    questions: pandas.DataFrame | None = None
    values = list(map(lambda value: value * (round_index + 1), VALUES))
    dailies = choices(values, weights=[0.24, 16.94, 53.94, 74.94, 53.94]) if dd else []

    for value in values:
        unselected = category.drop(
            [] if questions is None else questions["original_index"].tolist()
        )
        filtered = unselected[unselected["value"] == value]
        if filtered.empty:
            question = unselected.sample(n=1)
            question["value"] = value
        else:
            question = filtered.sample(n=1)
        question["original_index"] = question.index
        question["dd"] = value in dailies

        if questions is None:
            questions = question
        else:
            questions.loc[len(questions)] = question.iloc[0]

    return (
        [Question(question) for question in questions.to_dict("records")]
        if questions is not None
        else []
    )
