# IEvaluationProvider.py
from abc import ABC, abstractmethod
from CoreDomainModel.EvaluationResult import EvaluationResult
from CoreDomainModel.Code import Code


class IEvaluationProvider(ABC):

    @abstractmethod
    def evaluate(self, secret: Code, guess: Code) -> EvaluationResult:
        pass
