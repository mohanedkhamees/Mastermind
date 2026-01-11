from typing import List
from CoreDomainModel.Round import Round
from CoreDomainModel.GameState import GameState
from CoreDomainModel.GameVariant import GameVariant


class Game:
    def __init__(self, variant: GameVariant, max_rounds: int = 10):
        self._variant = variant
        self._max_rounds = max_rounds
        self._rounds: List[Round] = []
        self._state = GameState.NOT_STARTED

    def start(self):
        self._state = GameState.RUNNING

    def add_round(self, round_: Round):
        if self._state != GameState.RUNNING:
            raise RuntimeError("Game is not running")

        self._rounds.append(round_)

        if len(self._rounds) >= self._max_rounds:
            self._state = GameState.LOST

    def get_rounds(self) -> List[Round]:
        return self._rounds

    def get_state(self) -> GameState:
        return self._state

    def get_variant(self) -> GameVariant:
        return self._variant

    def has_rounds_left(self) -> bool:
        return len(self._rounds) < self._max_rounds

    def get_max_rounds(self) -> int:
        return self._max_rounds