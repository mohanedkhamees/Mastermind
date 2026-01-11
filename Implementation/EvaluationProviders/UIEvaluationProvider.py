# UIEvaluationProvider.py
from typing import Optional
from threading import Event
from CoreDomainModel.IEvaluationProvider import IEvaluationProvider
from CoreDomainModel.EvaluationResult import EvaluationResult


class UIEvaluationProvider(IEvaluationProvider):
    """Evaluation provider that waits for UI feedback."""

    def __init__(self):
        self._feedback_event = Event()
        self._feedback: Optional[EvaluationResult] = None

    def set_feedback(self, black: int, white: int) -> None:
        self._feedback = EvaluationResult(black, white)
        self._feedback_event.set()

    def evaluate(self, secret, guess):
        self._feedback_event.clear()
        self._feedback_event.wait()
        result = self._feedback
        self._feedback = None
        return result
