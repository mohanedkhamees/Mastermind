from abc import ABC, abstractmethod
from typing import Optional
from CoreDomainModel.Code import Code
from CoreDomainModel.EvaluationResult import EvaluationResult
from CoreDomainModel.GameVariant import GameVariant


class NetworkService(ABC):

    @abstractmethod
    def start_new_game(self, variant: GameVariant, secret_code: Code) -> Optional[str]:
        pass

    @abstractmethod
    def start_remote_game(self, variant: GameVariant) -> Optional[int]:
        pass

    @abstractmethod
    def evaluate_guess(self, guess: Code) -> Optional[EvaluationResult]:
        pass
