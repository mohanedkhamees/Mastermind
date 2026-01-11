# UI1/Components/InputBar.py
from typing import List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton
from UI.Components.SlotButton import SlotButton
from UI.Components.ColorDotButton import ColorDotButton
from UI.Utils.ColorMapper import PALETTE_SUPERHIRN


class InputBar(QFrame):
    submitted = Signal(list)  # list[QColor]

    def __init__(self, cols: int = 4, palette: List[QColor] = None, parent=None):
        super().__init__(parent)
        self.cols = cols
        self.palette = palette or PALETTE_SUPERHIRN
        self.slots: List[SlotButton] = []
        self.slot_values: List[Optional[QColor]] = [None] * cols

        self.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.08);
                border: 2px solid rgba(170, 150, 255, 0.3);
                border-radius: 20px;
                padding: 8px;
            }
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(18)

        # Slots
        slots_wrap = QHBoxLayout()
        slots_wrap.setSpacing(10)
        for i in range(cols):
            s = SlotButton(i)
            s.clicked.connect(lambda _, k=i: self.clear_from(k))
            self.slots.append(s)
            slots_wrap.addWidget(s)
        root.addLayout(slots_wrap)

        # Add spacing between slots and palette
        root.addSpacing(24)

        # Palette
        pal_wrap = QHBoxLayout()
        pal_wrap.setSpacing(8)
        for i, col in enumerate(self.palette):
            b = ColorDotButton(col, i)
            b.clicked.connect(lambda _, c=col: self.add_color(c))
            pal_wrap.addWidget(b)
        root.addLayout(pal_wrap)

        root.addStretch(1)

        # Submit button
        submit_btn = QPushButton("Submit")
        submit_btn.setObjectName("Primary")
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.setFixedHeight(38)
        submit_btn.clicked.connect(self.submit)
        root.addWidget(submit_btn)

        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("Ghost")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setFixedHeight(38)
        clear_btn.clicked.connect(self.clear_all)
        root.addWidget(clear_btn)

    def add_color(self, color: QColor):
        try:
            idx = self.slot_values.index(None)
        except ValueError:
            return
        self.slot_values[idx] = color
        self.slots[idx].set_color(color)

    def clear_all(self):
        self.slot_values = [None] * self.cols
        for s in self.slots:
            s.set_color(None)

    def clear_from(self, idx: int):
        for i in range(idx, self.cols):
            self.slot_values[i] = None
            self.slots[i].set_color(None)

    def submit(self):
        if None not in self.slot_values:
            colors = [c for c in self.slot_values if c is not None]
            self.submitted.emit(colors)
            self.clear_all()

    def set_enabled(self, enabled: bool):
        for s in self.slots:
            s.setEnabled(enabled)
        self.setEnabled(enabled)