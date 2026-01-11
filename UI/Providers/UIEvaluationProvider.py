# UI1/Providers1/UIEvaluationProvider.py
from typing import Optional
from threading import Event
from CoreDomainModel.IEvaluationProvider import IEvaluationProvider
from CoreDomainModel.EvaluationResult import EvaluationResult
from CoreDomainModel.Code import Code


class UIEvaluationProvider(IEvaluationProvider):
    """Evaluation provider that waits for UI1 input"""

    def __init__(self):
        self._feedback_event = Event()
        self._current_result: Optional[EvaluationResult] = None

    def set_feedback(self, black: int, white: int):
        """Called by UI1 when user provides feedback"""
        self._current_result = EvaluationResult(black, white)
        self._feedback_event.set()

    def evaluate(self, secret: Code, guess: Code) -> EvaluationResult:
        """Called by GameController - blocks until UI1 provides feedback"""
        self._feedback_event.clear()
        self._feedback_event.wait()
        result = self._current_result
        self._current_result = None
        return result