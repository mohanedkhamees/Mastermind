# UI1/Components/BoardWidget.py
from typing import List
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QBrush, QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from CoreDomainModel.GameVariant import GameVariant
from UI.Components.GuessRowWidget import GuessRowWidget


class BoardWidget(QWidget):
    """Game board showing all guess rows"""

    def __init__(self, variant: GameVariant, label: str, parent=None):
        super().__init__(parent)
        self.variant = variant
        self.label = label
        self.is_active = False
        self.rows: List[GuessRowWidget] = []
        self.current_row_idx = 0

        self.setMinimumSize(360, 560)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(8)

        # Title
        title = QLabel(label)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: rgba(240, 240, 255, 210);")
        title.setAlignment(Qt.AlignHCenter)
        layout.addWidget(title)

        # Rows - Always 10 rows
        self.rows_container = QWidget()
        rows_layout = QVBoxLayout(self.rows_container)
        rows_layout.setContentsMargins(0, 0, 0, 0)
        rows_layout.setSpacing(6)

        max_rounds = 10
        for _ in range(max_rounds):
            row = GuessRowWidget(variant.code_length)
            self.rows.append(row)
            rows_layout.addWidget(row)

        layout.addWidget(self.rows_container)
        layout.addStretch()

    def set_active(self, active: bool):
        self.is_active = active
        self.update()

    def add_round(self, guess_colors: List[QColor], black: int, white: int):
        """Add a completed round to the board"""
        if self.current_row_idx < len(self.rows):
            row = self.rows[self.current_row_idx]
            row.set_guess(guess_colors)
            row.set_feedback(black, white)
            self.current_row_idx += 1
            # Force update
            row.update()
            self.update()

    def clear(self):
        """Clear all rounds"""
        self.current_row_idx = 0
        for row in self.rows:
            row.set_guess([])
            row.set_feedback(0, 0)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        rect = self.rect().adjusted(18, 18, -18, -18)
        border_alpha = 70 if self.is_active else 30
        p.setPen(QPen(QColor(220, 210, 255, border_alpha), 2 if self.is_active else 1))
        p.setBrush(QBrush(QColor(255, 255, 255, 10)))
        p.drawRoundedRect(rect, 22, 22)