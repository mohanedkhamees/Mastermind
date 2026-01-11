# UI1/Providers1/UISecretCodeProvider.py
from typing import Optional
from threading import Event
from CoreDomainModel.ISecretCodeProvider import ISecretCodeProvider
from CoreDomainModel.Code import Code
from CoreDomainModel.PegColor import PegColor


class UISecretCodeProvider(ISecretCodeProvider):
    """Secret code provider that waits for UI1 input"""

    def __init__(self):
        self._code_event = Event()
        self._current_code: Optional[Code] = None
        self._code_set = False

    def set_code(self, pegs: list[PegColor]):
        """Called by UI1 when user creates secret code"""
        self._current_code = Code(pegs)
        self._code_set = True
        self._code_event.set()

    def create_secret_code(self) -> Code:
        """Called by GameController - blocks until UI1 provides code"""
        # If code was already set, return it immediately
        if self._code_set and self._current_code is not None:
            code = self._current_code
            self._current_code = None
            self._code_set = False
            self._code_event.clear()
            return code

        # Otherwise wait for code
        self._code_event.clear()
        self._code_event.wait()
        if self._current_code is None:
            raise RuntimeError("Code was not set properly")
        code = self._current_code
        self._current_code = None
        self._code_set = False
        return code