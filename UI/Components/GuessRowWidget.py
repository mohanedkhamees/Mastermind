# UI1/Components/GuessRowWidget.py
from typing import List, Optional
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QHBoxLayout
from UI.Components.SlotButton import SlotButton
from UI.Components.FeedbackPeg import FeedbackPeg


class GuessRowWidget(QWidget):
    """A single row showing guess pegs and feedback"""

    def __init__(self, peg_count: int, parent=None):
        super().__init__(parent)
        self.peg_count = peg_count
        self.guess_colors: List[Optional[QColor]] = [None] * peg_count
        self.feedback_black = 0
        self.feedback_white = 0

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(12)

        # Guess pegs
        self.guess_pegs: List[SlotButton] = []
        for i in range(peg_count):
            peg = SlotButton(i)
            peg.setEnabled(False)  # Read-only in game view
            self.guess_pegs.append(peg)
            layout.addWidget(peg)

        layout.addSpacing(20)

        # Feedback pegs in two rows (2 pegs per row)
        from PySide6.QtWidgets import QVBoxLayout
        feedback_container = QWidget()
        feedback_main_layout = QVBoxLayout(feedback_container)
        feedback_main_layout.setContentsMargins(0, 0, 0, 0)
        feedback_main_layout.setSpacing(4)
        
        # Create two rows
        row1_layout = QHBoxLayout()
        row1_layout.setContentsMargins(0, 0, 0, 0)
        row1_layout.setSpacing(4)
        row2_layout = QHBoxLayout()
        row2_layout.setContentsMargins(0, 0, 0, 0)
        row2_layout.setSpacing(4)
        
        self.feedback_pegs: List[FeedbackPeg] = []
        # Calculate pegs per row: first row gets 2, rest goes to second row
        pegs_per_row1 = 2
        for i in range(peg_count):
            fb = FeedbackPeg()
            self.feedback_pegs.append(fb)
            # Distribute pegs across two rows (2 in first row, rest in second row)
            if i < pegs_per_row1:
                row1_layout.addWidget(fb)
            else:
                row2_layout.addWidget(fb)
        
        feedback_main_layout.addLayout(row1_layout)
        feedback_main_layout.addLayout(row2_layout)
        layout.addWidget(feedback_container)

        layout.addStretch()

    def set_guess(self, colors: List[QColor]):
        for i, color in enumerate(colors):
            if i < len(self.guess_pegs):
                self.guess_pegs[i].set_color(color)

    def set_feedback(self, black: int, white: int):
        self.feedback_black = black
        self.feedback_white = white

        # Set black pegs first, then white
        idx = 0
        for _ in range(black):
            if idx < len(self.feedback_pegs):
                self.feedback_pegs[idx].set_feedback("black")
                idx += 1
        for _ in range(white):
            if idx < len(self.feedback_pegs):
                self.feedback_pegs[idx].set_feedback("white")
                idx += 1
        # Clear remaining
        while idx < len(self.feedback_pegs):
            self.feedback_pegs[idx].set_feedback(None)
            idx += 1