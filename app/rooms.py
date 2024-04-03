from os import urandom
from random import choices
import string

from werkzeug.datastructures import ImmutableMultiDict

from .app import socket
from .util import CATEGORIES, ROUNDS, TOTAL_QUESTIONS, VALUES, Answer, Round
from .questions import Question, pick_questions, questions_df


class Player:
    def __init__(self, name):
        self.name: str = name.strip().upper()
        self.money: float = 0
        self.id = urandom(20).hex()
        self.sid: str | None = None

    def answer_question(self, question_id: int, answer: Answer):
        value = questions_df.iloc[question_id].value
        if answer == Answer.Gain:
            self.money += value
        elif answer == Answer.Loss:
            self.money -= value

    def send(self, message):
        if not self.sid:
            return False
        socket.send(message, to=self.sid)
        return True


rooms: "dict[str, Room]" = {}


def generate_room_id():
    room_id = None
    while room_id is None or room_id in rooms:
        room_id = "".join(choices(string.ascii_uppercase + string.digits, k=6))
    return room_id


class Room:
    def __init__(self, form: "ImmutableMultiDict[str, str]"):
        self.id = generate_room_id()
        self.done_questions: list[int] = []
        self.questions: list[list[Question]] = []
        self.round_index: Round = Round.Lobby
        self.voice = form.get("voice")
        self.players: list[Player] = []
        self.host = urandom(20).hex()
        self.host_sid: str | None = None
        rooms[self.id] = self

    @property
    def round_name(self):
        return (0 <= self.round_index < len(ROUNDS)) and ROUNDS[self.round_index]

    @property
    def available_question_indicies(self):
        return [question.original_index for question in self.available_questions]

    @property
    def available_questions(self):
        return [
            question
            for category in self.questions
            for question in category
            if question.original_index not in self.done_questions
        ]

    def sort_players(self):
        self.players = sorted(
            self.players,
            key=lambda player: player.money,
            reverse=True,
        )

    def send(self, message):
        count = 0

        if self.host_sid:
            socket.send(message, to=self.host_sid)
        else:
            count += 1

        for player in self.players:
            if not player.send(message):
                count += 1

        return count

    def refresh_questions(self):
        if len(self.done_questions) != TOTAL_QUESTIONS and self.round_index not in (
            Round.Lobby,
            Round.End,
        ):
            return

        self.done_questions = []

        match self.round_index:
            case Round.Lobby:
                self.round_index = Round.Jeopardy
            case Round.Jeopardy:
                self.round_index = Round.DoubleJeopardy
            case Round.DoubleJeopardy:
                self.round_index = Round.FinalJeopardy
                self.sort_players()
            case Round.FinalJeopardy:
                self.round_index = Round.End
                self.sort_players()

        self.load_questions()

    def load_questions(self):
        round_index = self.round_index
        if round_index in (Round.Lobby, Round.End):
            self.questions = []
            return

        round_questions = questions_df[questions_df["round"] == self.round_name]
        if round_index == Round.FinalJeopardy:
            questions = round_questions.sample(n=1)
            questions["original_index"] = questions.index
            self.questions = [
                [Question(question) for question in questions.to_dict("records")]
            ]
            return

        categories = round_questions["category"].value_counts()
        groups = categories[categories >= len(VALUES)].sample(n=CATEGORIES)
        dailies = groups.sample(n=round_index + 1).index
        questions = (
            round_questions[round_questions["category"].isin(groups.index)]
            .groupby("category")
            .apply(
                lambda category: pick_questions(
                    category,
                    round_index,
                    (category["category"].iloc[0]) in dailies,
                )
            )
        )
        self.questions = list(zip(*questions))

    def handle_wagers(self, form: ImmutableMultiDict[str, str]):
        guesses = map(
            lambda player: (
                player[1],
                form.get(f"guess-{player[0]}", False, type=bool),
                form.get(f"wager-{player[0]}", 0, type=float),
            ),
            enumerate(self.players),
        )
        for player, guess, wager in guesses:
            if guess:
                player.money += wager
            else:
                player.money -= wager
