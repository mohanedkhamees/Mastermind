# IAlgorithm.py
from abc import ABC, abstractmethod
from CoreDomainModel.Code import Code
from CoreDomainModel.EvaluationResult import EvaluationResult


class IAlgorithm(ABC):

    @abstractmethod
    def evaluate(self, secret: Code, guess: Code) -> EvaluationResult:
        pass
