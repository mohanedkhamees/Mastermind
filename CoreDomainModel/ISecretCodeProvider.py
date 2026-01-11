# ISecretCodeProvider.py
from abc import ABC, abstractmethod
from typing import List
from CoreDomainModel.Code import Code


class ISecretCodeProvider(ABC):

    @abstractmethod
    def create_secret_code(self) -> Code:
        pass

    def set_code(self, colors: List[str]) -> None:
        """Optionally accept a secret code as color names."""
        raise NotImplementedError
