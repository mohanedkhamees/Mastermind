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
