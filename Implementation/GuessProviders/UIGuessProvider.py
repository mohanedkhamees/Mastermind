# UIGuessProvider.py
from typing import Optional, List
from threading import Event
from CoreDomainModel.IGuessProvider import IGuessProvider
from CoreDomainModel.Code import Code


class UIGuessProvider(IGuessProvider):
    """Guess provider that waits for UI input via signal/event."""

    def __init__(self):
        self._guess_event = Event()
        self._current_guess: Optional[Code] = None

    def set_guess(self, pegs: List[str]) -> None:
        self._current_guess = Code.from_color_names(pegs)
        self._guess_event.set()

    def next_guess(self) -> Code:
        self._guess_event.clear()
        self._guess_event.wait()
        guess = self._current_guess
        self._current_guess = None
        return guess

    def update(self, guess: Code, result):
        pass

    def is_consistent(self) -> bool:
        return True
