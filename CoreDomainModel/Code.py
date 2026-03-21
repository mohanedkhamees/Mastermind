# Code.py
from typing import List
from CoreDomainModel.PegColor import PegColor


class Code:
    def __init__(self, pegs: List[PegColor]):
        self._pegs = pegs

    def get_pegs(self) -> List[PegColor]:
        return self._pegs

    def length(self) -> int:
        return len(self._pegs)

    @staticmethod
    def from_color_names(names: List[str]) -> "Code":
        pegs = [PegColor[name] for name in names]
        return Code(pegs)

    def to_color_names(self) -> List[str]:
        return [peg.name for peg in self._pegs]
