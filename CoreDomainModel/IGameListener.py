from abc import ABC, abstractmethod
from CoreDomainModel.Code import Code
from CoreDomainModel.EvaluationResult import EvaluationResult


class IGameListener(ABC):

    @abstractmethod
    def on_round_played(self, guess: Code, result: EvaluationResult):
        pass

    @abstractmethod
    def on_game_won(self):
        pass

    @abstractmethod
    def on_game_lost(self):
        pass
