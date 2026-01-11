# UI1/Providers1/UIGuessProvider.py
from typing import Optional
from threading import Event
from CoreDomainModel.IGuessProvider import IGuessProvider
from CoreDomainModel.Code import Code
from CoreDomainModel.PegColor import PegColor


class UIGuessProvider(IGuessProvider):
    """Guess provider that waits for UI1 input via signal/event"""

    def __init__(self):
        self._guess_event = Event()
        self._current_guess: Optional[Code] = None

    def set_guess(self, pegs: list[PegColor]):
        """Called by UI1 when user submits a guess"""
        self._current_guess = Code(pegs)
        self._guess_event.set()

    def next_guess(self) -> Code:
        """Called by GameController - blocks until UI1 provides guess"""
        self._guess_event.clear()
        self._guess_event.wait()  # Wait for UI1 input
        guess = self._current_guess
        self._current_guess = None
        return guess

    def update(self, guess: Code, result):
        pass

    def is_consistent(self) -> bool:
        return True