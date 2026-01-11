import random
from CoreDomainModel.ISecretCodeProvider import ISecretCodeProvider
from CoreDomainModel.Code import Code
from CoreDomainModel.PegColor import PegColor
from CoreDomainModel.GameVariant import GameVariant


class SystemSecretCodeProvider(ISecretCodeProvider):

    def __init__(self, variant: GameVariant):
        self._variant = variant

    def create_secret_code(self) -> Code:
        colors = list(PegColor)[:self._variant.color_count]
        pegs = random.choices(colors, k=self._variant.code_length)
        return Code(pegs)
