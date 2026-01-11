from CoreDomainModel.Code import Code
from CoreDomainModel.EvaluationResult import EvaluationResult


class Round:
    def __init__(self, guess: Code, result: EvaluationResult):
        self.guess = guess
        self.result = result
