# ISecretCodeProvider.py
from abc import ABC, abstractmethod
from CoreDomainModel.Code import Code


class ISecretCodeProvider(ABC):

    @abstractmethod
    def create_secret_code(self) -> Code:
        pass
