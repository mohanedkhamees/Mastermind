# IGame.py
from abc import ABC, abstractmethod
from CoreDomainModel.GameState import GameState


class IGame(ABC):

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def get_state(self) -> GameState:
        pass
