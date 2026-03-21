# IEvaluationProvider.py
from abc import ABC, abstractmethod
from CoreDomainModel.EvaluationResult import EvaluationResult
from CoreDomainModel.Code import Code


class IEvaluationProvider(ABC):

    @abstractmethod
    def evaluate(self, secret: Code, guess: Code) -> EvaluationResult:
        pass

    def set_feedback(self, black: int, white: int) -> None:
        """Optionally accept feedback for a computer guess."""
        raise NotImplementedError

    def uses_remote_secret(self) -> bool:
        """Return True when the secret code is not locally available."""
        return False
