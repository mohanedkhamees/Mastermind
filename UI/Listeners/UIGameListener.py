# UI/Listeners/UIGameListener.py
from PySide6.QtCore import QObject, Signal
from CoreDomainModel.IGameListener import IGameListener
from CoreDomainModel.Code import Code
from CoreDomainModel.EvaluationResult import EvaluationResult


class UIGameListener(QObject):
    """Adapter that connects GameController events to UI signals"""

    round_played = Signal(object, object)  # guess: Code, result: EvaluationResult
    game_won = Signal()
    game_lost = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    # Implement IGameListener interface methods
    def on_round_played(self, guess: Code, result: EvaluationResult):
        """Implement IGameListener interface"""
        self.round_played.emit(guess, result)

    def on_game_won(self):
        """Implement IGameListener interface"""
        self.game_won.emit()

    def on_game_lost(self):
        """Implement IGameListener interface"""
        self.game_lost.emit()