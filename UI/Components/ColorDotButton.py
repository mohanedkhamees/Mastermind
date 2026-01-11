# UI1/Components/ColorDotButton.py
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QBrush, QColor
from PySide6.QtWidgets import QPushButton


class ColorDotButton(QPushButton):
    def __init__(self, color: QColor, idx: int, parent=None):
        super().__init__(parent)
        self.color = color
        self.idx = idx
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(34, 34)
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        r = self.rect().adjusted(4, 4, -4, -4)
        p.setPen(QPen(QColor(255, 255, 255, 80), 2))
        p.setBrush(QBrush(self.color))
        p.drawEllipse(r)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(0, 0, 0, 30)))
        p.drawEllipse(r.adjusted(10, 10, -10, -10))