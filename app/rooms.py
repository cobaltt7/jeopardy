from random import choices, shuffle
import string

from pandas import Series
from werkzeug.datastructures import ImmutableMultiDict

from .users import Host, Player
from .util import CATEGORIES, ROUNDS, VALUES, Round
from .questions import Question, pick_questions, questions_df

rooms: "dict[str, Room]" = {}


def generate_room_id():
    room_id = None
    while room_id is None or room_id in rooms:
        room_id = "".join(choices(string.ascii_uppercase + string.digits, k=6))
    return room_id


class Room:
    def __init__(self):
        self.id = generate_room_id()
        rooms[self.id] = self
        self.round_index: Round = Round.Lobby

        self.host = Host()
        self.all_players: list[Player] = []
        self._current_auth_key: str | None = None

        self.questions: list[list[Question]] = []
        self.question_index: dict[int, Question] = {}
        self.current_question: int | None = None
        self.done_questions: list[int] = []

    @property
    def round_name(self):
        return ROUNDS[self.round_index] if 0 <= self.round_index < len(ROUNDS) else None

    @property
    def available_questions(self):
        return [
            question.original_index
            for category in self.questions
            for question in category
            if question.original_index not in self.done_questions
        ]

    @property
    def players(self):
        if self.round_index is Round.End:
            return sorted(
                self.all_players, key=lambda player: player.money, reverse=True
            )
        if self.round_index is Round.FinalJeopardy:
            return sorted(
                [player for player in self.all_players if player.money > 0],
                key=lambda player: player.money,
                reverse=True,
            )

        return self.all_players

    @property
    def current_player(self):
        return next(
            (
                player
                for player in self.all_players
                if player.auth_key == self._current_auth_key
            ),
            self.players[0],
        )

    @current_player.setter
    def current_player(self, player):
        self._current_auth_key = player.auth_key

    def emit(self, message, exclude: str | None = None):
        for player in self.all_players + [self.host]:
            if not exclude or exclude != player.auth_key:
                player.emit(message)

    def refresh_questions(self):
        if self.available_questions:
            return

        self.done_questions = []

        if self.round_index == Round.Lobby:
            shuffle(self.all_players)

        self.round_index = Round(self.round_index.value + 1)
        # TDO: end

        self.load_questions()

    def load_questions(self):
        round_index = self.round_index
        if round_index in (Round.Lobby, Round.End):
            self.questions = []
            return

        round_questions = questions_df.loc[questions_df["round"] == self.round_name]
        if round_index is Round.FinalJeopardy:
            final = round_questions.sample(n=1)
            final["original_index"] = final.index
            final["wager"] = True
            self.questions = [[]]
            for raw_question in final.to_dict("records"):
                question = Question(raw_question)
                self.questions[0].append(question)
                self.question_index[question.original_index] = question
            return

        categories = round_questions["category"].value_counts()
        selected_categories = categories.loc[categories >= len(VALUES)].sample(
            n=CATEGORIES
        )
        dailies = selected_categories.sample(n=round_index + 1).index

        selected_questions = round_questions[
            round_questions["category"].isin(selected_categories.index)
        ]
        questions_by_category = selected_questions.groupby("category")
        picked_questions: Series[list[Question]] = questions_by_category.apply(  # type: ignore
            lambda category: pick_questions(
                category, round_index, category["category"].iloc[0] in dailies
            )
        )

        self.questions = list(zip(*picked_questions))
        self.question_index.update({
            question.original_index: question
            for category in picked_questions
            for question in category
        })

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
