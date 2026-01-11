# IBoundary.py
# UI1/IBoundary.py
from abc import ABC, abstractmethod
from typing import List, Optional, Callable
from CoreDomainModel.GameVariant import GameVariant
from CoreDomainModel.Code import Code
from CoreDomainModel.EvaluationResult import EvaluationResult
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget


class IGameView(ABC):
    """Interface for displaying game state"""

    @abstractmethod
    def display_round(self, guess: Code, result: EvaluationResult, round_number: int):
        """Display a completed round with guess and feedback"""
        pass

    @abstractmethod
    def clear_all_rounds(self):
        """Clear all displayed rounds"""
        pass

    @abstractmethod
    def get_widget(self) -> QWidget:
        """Get the underlying widget for layout"""
        pass


class IInputView(ABC):
    """Interface for user input"""

    @abstractmethod
    def set_on_submit_callback(self, callback: Callable[[List[QColor]], None]):
        """Set callback when user submits input"""
        pass

    @abstractmethod
    def set_enabled(self, enabled: bool):
        """Enable/disable input"""
        pass

    @abstractmethod
    def clear(self):
        """Clear input fields"""
        pass

    @abstractmethod
    def get_widget(self) -> QWidget:
        """Get the underlying widget"""
        pass


class IFeedbackView(ABC):
    """Interface for feedback input (Kodierer mode)"""

    @abstractmethod
    def set_on_submit_callback(self, callback: Callable[[int, int], None]):
        """Set callback when feedback is submitted (black, white)"""
        pass

    @abstractmethod
    def show(self):
        """Show feedback input"""
        pass

    @abstractmethod
    def hide(self):
        """Hide feedback input"""
        pass

    @abstractmethod
    def reset(self):
        """Reset feedback values"""
        pass

    @abstractmethod
    def get_widget(self) -> QWidget:
        """Get the underlying widget"""
        pass


class ISecretCodeView(ABC):
    """Interface for displaying secret code"""

    @abstractmethod
    def display_code(self, colors: List[QColor]):
        """Display the secret code"""
        pass

    @abstractmethod
    def hide(self):
        """Hide the secret code display"""
        pass

    @abstractmethod
    def get_widget(self) -> QWidget:
        """Get the underlying widget"""
        pass


class ISettingsView(ABC):
    """Interface for settings screen"""

    @abstractmethod
    def get_variant(self) -> GameVariant:
        """Get selected game variant"""
        pass

    @abstractmethod
    def get_mode(self) -> str:
        """Get selected game mode (RATER, KODIERER, ZUSCHAUER)"""
        pass

    @abstractmethod
    def get_algorithm(self) -> str:
        """Get selected algorithm for single mode"""
        pass

    @abstractmethod
    def get_algorithm1(self) -> str:
        """Get algorithm for board 1 (Zuschauer mode)"""
        pass

    @abstractmethod
    def get_algorithm2(self) -> str:
        """Get algorithm for board 2 (Zuschauer mode)"""
        pass

    @abstractmethod
    def get_delay(self) -> int:
        """Get delay in seconds"""
        pass

    @abstractmethod
    def set_on_start_callback(self, callback: Callable[[], None]):
        """Set callback when start button is clicked"""
        pass

    @abstractmethod
    def get_widget(self) -> QWidget:
        """Get the underlying widget"""
        pass


class IGameScreen(ABC):
    """Interface for main game screen"""

    @abstractmethod
    def initialize_game(self, variant: GameVariant, mode: str):
        """Initialize game with variant and mode"""
        pass

    @abstractmethod
    def display_round(self, guess: Code, result: EvaluationResult, board: int = 0):
        """Display a completed round"""
        pass

    @abstractmethod
    def show_computer_guess(self, guess: Code):
        """Show computer's guess (for Kodierer mode)"""
        pass

    @abstractmethod
    def show_game_won(self, rounds: int, board: int = 0):
        """Show game won message"""
        pass

    @abstractmethod
    def show_game_lost(self, rounds: int, board: int = 0):
        """Show game lost message"""
        pass

    @abstractmethod
    def update_status(self, message: str):
        """Update status message"""
        pass

    @abstractmethod
    def set_on_back_callback(self, callback: Callable[[], None]):
        """Set callback for back button"""
        pass

    @abstractmethod
    def get_widget(self) -> QWidget:
        """Get the underlying widget"""
        pass