# UI1/Threads/GameThread.py
from PySide6.QtCore import QThread, Signal
from ApplicationControl.IBoundary import IBoundary


class GameThread(QThread):
    """Thread for running game asynchronously"""
    finished = Signal()
    error = Signal(str)
    computer_guessed = Signal(object)
    waiting_for_feedback = Signal()

    def __init__(self, boundary: IBoundary, parent=None):
        super().__init__(parent)
        self.boundary = boundary

    def run(self):
        try:
            self.boundary.play()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()
