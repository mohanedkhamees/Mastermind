# HumanGuessProvider.py
from CoreDomainModel.IGuessProvider import IGuessProvider
from CoreDomainModel.Code import Code
from CoreDomainModel.PegColor import PegColor


class HumanGuessProvider(IGuessProvider):

    def next_guess(self) -> Code:
        raw = input("Enter your guess as numbers separated by spaces (e.g. 1 2 3 4): ")
        values = raw.strip().split()

        pegs = [PegColor(int(v)) for v in values]
        return Code(pegs)

    def update(self, guess: Code, result):
        # Human does not need to learn from feedback
        pass

    def is_consistent(self) -> bool:
        return True

    def set_guess(self, pegs):
        pass
