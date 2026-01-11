from typing import Any, Callable, Dict, List, Optional
from ApplicationControl.IBoundary import IBoundary
from CoreDomainModel.IGame import IGame


class GameController(IBoundary):
    """Boundary implementation connecting UI to the game."""

    def __init__(self, game: IGame):
        self._game = game
        self._on_round_played: Optional[Callable[[Dict[str, Any]], None]] = None
        self._on_game_won: Optional[Callable[[Dict[str, Any]], None]] = None
        self._on_game_lost: Optional[Callable[[Dict[str, Any]], None]] = None
        self._on_computer_guess: Optional[Callable[[Dict[str, Any]], None]] = None
        self._on_waiting_for_feedback: Optional[Callable[[Dict[str, Any]], None]] = None
        self._game.set_event_sink(self)

    def start_new_game(self, config: Dict[str, Any]) -> bool:
        return self._game.start(config)

    def play(self) -> None:
        self._game.play()

    def submit_guess(self, colors: List[str]) -> None:
        self._game.submit_guess(colors)

    def submit_feedback(self, black: int, white: int) -> None:
        self._game.submit_feedback(black, white)

    def submit_secret_code(self, colors: List[str]) -> None:
        self._game.submit_secret_code(colors)

    def step(self) -> None:
        self._game.step()

    def get_game_view(self) -> Dict[str, Any]:
        return self._game.get_view()

    def set_on_round_played(self, callback: Optional[Callable[[Dict[str, Any]], None]]) -> None:
        self._on_round_played = callback

    def set_on_game_won(self, callback: Optional[Callable[[Dict[str, Any]], None]]) -> None:
        self._on_game_won = callback

    def set_on_game_lost(self, callback: Optional[Callable[[Dict[str, Any]], None]]) -> None:
        self._on_game_lost = callback

    def set_on_computer_guess(self, callback: Optional[Callable[[Dict[str, Any]], None]]) -> None:
        self._on_computer_guess = callback

    def set_on_waiting_for_feedback(self, callback: Optional[Callable[[Dict[str, Any]], None]]) -> None:
        self._on_waiting_for_feedback = callback

    def on_round_played(self, payload: Dict[str, Any]) -> None:
        if self._on_round_played:
            self._on_round_played(payload)

    def on_game_won(self, payload: Dict[str, Any]) -> None:
        if self._on_game_won:
            self._on_game_won(payload)

    def on_game_lost(self, payload: Dict[str, Any]) -> None:
        if self._on_game_lost:
            self._on_game_lost(payload)

    def on_computer_guess(self, payload: Dict[str, Any]) -> None:
        if self._on_computer_guess:
            self._on_computer_guess(payload)

    def on_waiting_for_feedback(self, payload: Dict[str, Any]) -> None:
        if self._on_waiting_for_feedback:
            self._on_waiting_for_feedback(payload)
