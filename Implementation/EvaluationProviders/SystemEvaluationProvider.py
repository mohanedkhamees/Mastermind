# SystemEvaluationProvider.py
from CoreDomainModel.IEvaluationProvider import IEvaluationProvider
from CoreDomainModel.Code import Code
from CoreDomainModel.EvaluationResult import EvaluationResult
from collections import Counter


class SystemEvaluationProvider(IEvaluationProvider):

    def evaluate(self, secret: Code, guess: Code) -> EvaluationResult:
        secret_pegs = secret.get_pegs()
        guess_pegs = guess.get_pegs()

        if len(secret_pegs) != len(guess_pegs):
            raise ValueError("Secret and guess must have the same length")

        # 1. Count correct positions (black pegs)
        black = 0
        remaining_secret = []
        remaining_guess = []

        for s, g in zip(secret_pegs, guess_pegs):
            if s == g:
                black += 1
            else:
                remaining_secret.append(s)
                remaining_guess.append(g)

        # 2. Count correct colors in wrong positions (white pegs)
        secret_counter = Counter(remaining_secret)
        guess_counter = Counter(remaining_guess)

        white = 0
        for color in guess_counter:
            white += min(guess_counter[color], secret_counter.get(color, 0))

        return EvaluationResult(black, white)
