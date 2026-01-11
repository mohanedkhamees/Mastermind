# Implementation/Algorithms/KnuthAlgorithm.py
import itertools
from typing import List
from CoreDomainModel.Code import Code
from CoreDomainModel.GameVariant import GameVariant
from CoreDomainModel.IEvaluationProvider import IEvaluationProvider
from CoreDomainModel.IGuessProvider import IGuessProvider
from CoreDomainModel.PegColor import PegColor
from CoreDomainModel.EvaluationResult import EvaluationResult


class KnuthAlgorithm(IGuessProvider):
    """
    Knuth's algorithm (1977) - Simplified Minimax strategy
    Optimized for performance while maintaining the core minimax principle
    """

    def __init__(self, variant: GameVariant, evaluation_provider: IEvaluationProvider):
        self._variant = variant
        self._evaluation_provider = evaluation_provider
        self._possible_codes: List[Code] = []
        self._all_codes: List[Code] = []
        self._guesses_made: List[Code] = []
        self._initialize()

    def _initialize(self):
        colors = list(PegColor)[:self._variant.color_count]
        combinations = itertools.product(colors, repeat=self._variant.code_length)

        self._all_codes = [Code(list(c)) for c in combinations]
        self._possible_codes = self._all_codes.copy()

    def _evaluate_guess(self, secret: Code, guess: Code) -> EvaluationResult:
        """Evaluate a guess against a secret code"""
        return self._evaluation_provider.evaluate(secret, guess)

    def _minimax_score_fast(self, guess: Code) -> int:
        """
        Fast minimax score calculation
        Only checks a sample of possible results to speed things up
        """
        max_remaining = 0
        max_pegs = self._variant.code_length

        # Sample key results instead of all combinations
        # This is much faster while still being effective
        key_results = [
            (0, 0),  # No matches
            (1, 0), (0, 1),  # One match
            (2, 0), (1, 1), (0, 2),  # Two matches
            (max_pegs, 0),  # All correct position
        ]

        for black, white in key_results:
            if black + white > max_pegs:
                continue

            result = EvaluationResult(black, white)
            remaining = 0

            # Count consistent codes (limit check for speed)
            check_limit = min(100, len(self._possible_codes))
            for candidate in self._possible_codes[:check_limit]:
                expected = self._evaluate_guess(candidate, guess)
                if (expected.correct_position == black and
                        expected.correct_color == white):
                    remaining += 1

            # Extrapolate if we limited the check
            if check_limit < len(self._possible_codes):
                remaining = int(remaining * (len(self._possible_codes) / check_limit))

            max_remaining = max(max_remaining, remaining)

        return max_remaining

    def next_guess(self) -> Code:
        if not self._possible_codes:
            raise RuntimeError("No possible codes left")

        # First guess: optimal starting guess
        if len(self._guesses_made) == 0:
            colors = list(PegColor)[:self._variant.color_count]
            if self._variant.code_length == 4:
                first_guess = Code([colors[0], colors[0], colors[1], colors[1]])
            elif self._variant.code_length == 5:
                first_guess = Code([colors[0], colors[0], colors[1], colors[1], colors[2]])
            else:
                first_guess = Code([colors[0], colors[0], colors[1], colors[1]] +
                                   [colors[0]] * (self._variant.code_length - 4))

            # Check if first_guess exists in _all_codes by comparing pegs
            first_pegs = first_guess.get_pegs()
            for code in self._all_codes:
                if code.get_pegs() == first_pegs:
                    self._guesses_made.append(first_guess)
                    return first_guess

        # Minimax strategy - but only check possible codes for speed
        best_guess = None
        best_score = float('inf')

        # Only check possible codes (not all codes) - much faster
        # Limit to first 200 for very large sets
        candidates = self._possible_codes[:200] if len(self._possible_codes) > 200 else self._possible_codes

        for guess in candidates:
            if guess in self._guesses_made:
                continue

            score = self._minimax_score_fast(guess)

            if score < best_score:
                best_score = score
                best_guess = guess

                # Early exit for very good score
                if best_score <= 2:
                    break

        # Fallback
        if best_guess is None:
            best_guess = self._possible_codes[0]

        self._guesses_made.append(best_guess)
        return best_guess

    def update(self, guess: Code, result: EvaluationResult):
        """Update possible codes based on feedback"""
        new_possible = []

        for candidate in self._possible_codes:
            expected = self._evaluate_guess(candidate, guess)

            if (expected.correct_position == result.correct_position and
                    expected.correct_color == result.correct_color):
                new_possible.append(candidate)

        self._possible_codes = new_possible

    def is_consistent(self) -> bool:
        return len(self._possible_codes) > 0