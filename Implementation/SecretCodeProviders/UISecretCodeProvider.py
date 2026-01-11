# UISecretCodeProvider.py
from typing import Optional, List
from threading import Event
from CoreDomainModel.ISecretCodeProvider import ISecretCodeProvider
from CoreDomainModel.Code import Code


class UISecretCodeProvider(ISecretCodeProvider):
    """Secret code provider that waits for UI input."""

    def __init__(self):
        self._code_event = Event()
        self._code: Optional[Code] = None

    def set_code(self, colors: List[str]) -> None:
        self._code = Code.from_color_names(colors)
        self._code_event.set()

    def create_secret_code(self) -> Code:
        self._code_event.clear()
        self._code_event.wait()
        code = self._code
        self._code = None
        return code
