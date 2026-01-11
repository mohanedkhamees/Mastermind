# UI1/Components/SlotButton.py
from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QBrush, QColor
from PySide6.QtWidgets import QPushButton


class SlotButton(QPushButton):
    def __init__(self, index: int, parent=None):
        super().__init__(parent)
        self.index = index
        self.color: Optional[QColor] = None
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(40, 40)
        self.setStyleSheet("background: transparent;")

    def set_color(self, c: Optional[QColor]):
        self.color = c
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        r = self.rect().adjusted(6, 6, -6, -6)
        p.setPen(QPen(QColor(255, 255, 255, 70), 2))
        if self.color is None:
            p.setBrush(QBrush(QColor(230, 230, 255, 28)))
        else:
            p.setBrush(QBrush(self.color))
        p.drawEllipse(r)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(0, 0, 0, 35)))
        p.drawEllipse(r.adjusted(10, 10, -10, -10))