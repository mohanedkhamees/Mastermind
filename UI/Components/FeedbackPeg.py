# UI1/Components/FeedbackPeg.py
from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QBrush, QColor
from PySide6.QtWidgets import QWidget


class FeedbackPeg(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self.color_type: Optional[str] = None  # "black", "white", or None

    def set_feedback(self, color_type: Optional[str]):
        self.color_type = color_type
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        r = self.rect().adjusted(1, 1, -1, -1)

        if self.color_type == "black":
            p.setPen(QPen(QColor(255, 255, 255, 100), 1))
            p.setBrush(QBrush(QColor(0, 0, 0)))
        elif self.color_type == "white":
            p.setPen(QPen(QColor(0, 0, 0, 100), 1))
            p.setBrush(QBrush(QColor(255, 255, 255)))
        else:
            p.setPen(QPen(QColor(255, 255, 255, 40), 1))
            p.setBrush(QBrush(QColor(235, 235, 245, 60)))

        # Draw circle (round)
        p.drawEllipse(r)