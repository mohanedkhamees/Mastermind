# UI1/Components/SecretCodeDisplay.py
from typing import List
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel
from UI.Components.SlotButton import SlotButton


class SecretCodeDisplay(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: rgba(170, 150, 255, 0.18);
                border: 2px solid rgba(170, 150, 255, 0.6);
                border-radius: 16px;
                padding: 16px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(16)

        # Label
        self.label = QLabel("🔒 Geheimer Code:")
        self.label.setStyleSheet("color: rgba(245,245,255,0.9); font-size: 14px; font-weight: bold;")
        layout.addWidget(self.label)

        # Pegs container
        self.pegs_layout = QHBoxLayout()
        self.pegs_layout.setSpacing(12)
        self.pegs: List[SlotButton] = []
        layout.addLayout(self.pegs_layout)

        layout.addStretch()

    def display_code(self, colors: List[QColor]):
        """Display the secret code"""
        # Clear old pegs
        for peg in self.pegs:
            peg.setParent(None)
        self.pegs.clear()

        # Create new pegs
        for i, color in enumerate(colors):
            peg = SlotButton(i)
            peg.set_color(color)
            peg.setEnabled(False)  # Read-only
            self.pegs.append(peg)
            self.pegs_layout.addWidget(peg)

    def hide(self):
        """Hide the secret code display"""
        self.setVisible(False)