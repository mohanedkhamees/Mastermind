# UI1/Threads/GameThread.py
from PySide6.QtCore import QThread, Signal
from ApplicationControl.GameController import GameController
from ApplicationControl.DelaySynchronizer import DelaySynchronizer
from CoreDomainModel.GameState import GameState as DomainGameState
from CoreDomainModel.Code import Code


class GameThread(QThread):
    """Thread for running game asynchronously"""
    finished = Signal()
    error = Signal(str)
    computer_guessed = Signal(object)
    waiting_for_feedback = Signal()

    def __init__(self, controller: GameController, parent=None, is_human_evaluator: bool = False, delay=None):
        super().__init__(parent)
        self.controller = controller
        self.is_human_evaluator = is_human_evaluator
        self.delay = delay

    def run(self):
        try:
            self.controller.start_game()

            variant = self.controller._game.get_variant()
            max_pegs = variant.code_length

            while (
                    self.controller._game.get_state() == DomainGameState.RUNNING
                    and self.controller._game.has_rounds_left()
            ):
                # Get next guess
                guess = self.controller._guess_provider.next_guess()

                if self.is_human_evaluator:
                    self.computer_guessed.emit(guess)
                    self.waiting_for_feedback.emit()

                # Evaluate guess
                result = self.controller._evaluation_provider.evaluate(
                    self.controller._secret_code, guess
                )

                # Validate
                if result.correct_position < 0 or result.correct_color < 0:
                    raise RuntimeError("Invalid feedback: negative values")

                if result.correct_position + result.correct_color > max_pegs:
                    raise RuntimeError("Invalid feedback: exceeds code length")

                # Update algorithm
                self.controller._guess_provider.update(guess, result)

                # Store round
                from CoreDomainModel.Round import Round
                self.controller._game.add_round(Round(guess, result))
                self.controller._notify_round(guess, result)

                # Check consistency
                if not self.controller._guess_provider.is_consistent():
                    raise RuntimeError("Inconsistent feedback")

                # Win?
                if result.is_correct(max_pegs):
                    self.controller._game._state = DomainGameState.WON
                    self.controller._notify_win()
                    return

                # Delay between rounds
                if self.delay:
                    self.delay.wait()
                elif not self.is_human_evaluator:
                    self.msleep(1000)

            # Loss
            if not self.controller._game.has_rounds_left():
                self.controller._game._state = DomainGameState.LOST
                self.controller._notify_loss()

        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()