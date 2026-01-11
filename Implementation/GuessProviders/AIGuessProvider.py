from CoreDomainModel.IGuessProvider import IGuessProvider
from CoreDomainModel.EvaluationResult import EvaluationResult
from CoreDomainModel.Code import Code


class AIGuessProvider(IGuessProvider):

    def __init__(self, algorithm: IGuessProvider):
        self._algorithm = algorithm

    def next_guess(self) -> Code:
        return self._algorithm.next_guess()

    def update(self, guess: Code, result: EvaluationResult):
        self._algorithm.update(guess, result)

    def is_consistent(self) -> bool:
            if hasattr(self._algorithm, "_possible_codes"):
                return len(self._algorithm._possible_codes) > 0
            return True

    def set_guess(self, pegs):
        pass
