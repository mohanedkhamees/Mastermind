# IGame.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IGame(ABC):

    @abstractmethod
    def start(self, config: Dict[str, Any]) -> bool:
        """Initialize a game using the provided config."""
        pass

    @abstractmethod
    def play(self) -> None:
        """Run the game loop until completion."""
        pass

    @abstractmethod
    def submit_guess(self, colors: List[str]) -> None:
        """Submit a human guess using color names."""
        pass

    @abstractmethod
    def submit_feedback(self, black: int, white: int) -> None:
        """Submit feedback for a computer guess."""
        pass

    @abstractmethod
    def submit_secret_code(self, colors: List[str]) -> None:
        """Submit a secret code for the computer to guess."""
        pass

    @abstractmethod
    def step(self) -> None:
        """Advance an auto-running game by one step."""
        pass

    @abstractmethod
    def get_view(self) -> Dict[str, Any]:
        """Return a view DTO for UI rendering."""
        pass

    @abstractmethod
    def set_event_sink(self, sink: Any) -> None:
        """Register an event sink for game events."""
        pass
