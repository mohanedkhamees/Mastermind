from abc import ABC, abstractmethod
from CoreDomainModel.Code import Code
from CoreDomainModel.EvaluationResult import EvaluationResult


class IGuessProvider(ABC):

    @abstractmethod
    def next_guess(self) -> Code:
        pass

    @abstractmethod
    def update(self, guess: Code, result: EvaluationResult):
        pass

    @abstractmethod
    def is_consistent(self) -> bool:
        """
        Returns False if no possible codes remain.
        """
        pass