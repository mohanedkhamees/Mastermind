# ConsistencyBasedAlgorithm.py
from typing import List, Tuple
from CoreDomainModel.IAlgorithm import IAlgorithm
from CoreDomainModel.Code import Code
from CoreDomainModel.EvaluationResult import EvaluationResult
from CoreDomainModel.GameVariant import GameVariant
from CoreDomainModel.IGuessProvider import IGuessProvider
from CoreDomainModel.PegColor import PegColor
from CoreDomainModel.IEvaluationProvider import IEvaluationProvider
import itertools

class ConsistencyBasedAlgorithm(IGuessProvider):

    def __init__(self, variant: GameVariant, evaluation_provider: IEvaluationProvider):
        self._variant = variant
        self._evaluation_provider = evaluation_provider
        self._possible_codes: List[Code] = self._generate_all_codes()
        self._history: List[Tuple[Code, EvaluationResult]] = []

    def _generate_all_codes(self) -> List[Code]:
        colors = list(PegColor)[:self._variant.color_count]
        combinations = itertools.product(colors, repeat=self._variant.code_length)
        return [Code(list(c)) for c in combinations]

    def _is_consistent(self, candidate: Code) -> bool:
        for guess, result in self._history:
            expected = self._evaluation_provider.evaluate(candidate, guess)
            if (expected.correct_position != result.correct_position or
                expected.correct_color != result.correct_color):
                return False
        return True

    def update(self, guess: Code, result: EvaluationResult):
        self._history.append((guess, result))
        self._possible_codes = [
            c for c in self._possible_codes if self._is_consistent(c)
        ]

    def next_guess(self) -> Code:
        if not self._possible_codes:
            raise RuntimeError("No possible codes left – inconsistent feedback")

        return self._possible_codes[0]

    def is_consistent(self) -> bool:
        return len(self._possible_codes) > 0
