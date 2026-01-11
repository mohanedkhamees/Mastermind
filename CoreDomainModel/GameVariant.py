from enum import Enum


class GameVariant(Enum):
    SUPERHIRN = (4, 6)
    SUPERSUPERHIRN = (5, 8)

    def __init__(self, code_length: int, color_count: int):
        self._code_length = code_length
        self._color_count = color_count

    @property
    def code_length(self) -> int:
        return self._code_length

    @property
    def color_count(self) -> int:
        return self._color_count
