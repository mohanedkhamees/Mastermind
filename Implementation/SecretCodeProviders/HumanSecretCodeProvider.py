from CoreDomainModel.ISecretCodeProvider import ISecretCodeProvider
from CoreDomainModel.Code import Code
from CoreDomainModel.PegColor import PegColor


class HumanSecretCodeProvider(ISecretCodeProvider):

    def create_secret_code(self) -> Code:
        raw = input("Enter secret code as numbers separated by spaces (e.g. 1 2 3 4): ")
        values = raw.strip().split()

        pegs = [PegColor(int(v)) for v in values]
        return Code(pegs)
