from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional


class IBoundary(ABC):

    @abstractmethod
    def start_new_game(self, config: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def play(self) -> None:
        pass

    @abstractmethod
    def submit_guess(self, colors: List[str]) -> None:
        pass

    @abstractmethod
    def submit_feedback(self, black: int, white: int) -> None:
        pass

    @abstractmethod
    def submit_secret_code(self, colors: List[str]) -> None:
        pass

    @abstractmethod
    def step(self) -> None:
        pass

    @abstractmethod
    def get_game_view(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def set_on_round_played(self, callback: Optional[Callable[[Dict[str, Any]], None]]) -> None:
        pass

    @abstractmethod
    def set_on_game_won(self, callback: Optional[Callable[[Dict[str, Any]], None]]) -> None:
        pass

    @abstractmethod
    def set_on_game_lost(self, callback: Optional[Callable[[Dict[str, Any]], None]]) -> None:
        pass

    @abstractmethod
    def set_on_computer_guess(self, callback: Optional[Callable[[Dict[str, Any]], None]]) -> None:
        pass

    @abstractmethod
    def set_on_waiting_for_feedback(self, callback: Optional[Callable[[Dict[str, Any]], None]]) -> None:
        pass
