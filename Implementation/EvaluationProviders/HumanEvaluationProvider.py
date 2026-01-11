from CoreDomainModel.IEvaluationProvider import IEvaluationProvider
from CoreDomainModel.EvaluationResult import EvaluationResult


class HumanEvaluationProvider(IEvaluationProvider):

    def evaluate(self, secret, guess) -> EvaluationResult:
        black = int(input("Enter number of correct positions (black pegs): "))
        white = int(input("Enter number of correct colors (white pegs): "))
        return EvaluationResult(black, white)
