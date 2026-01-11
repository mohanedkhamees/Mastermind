# UI1/Components/Segmented.py
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QButtonGroup, QFrame, QSizePolicy


class Segmented(QWidget):
    changed = Signal(int)

    def __init__(self, labels, *, fixed_width=320, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        self.group = QButtonGroup(self)
        self.group.setExclusive(True)

        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 14px;
            }
        """)
        c = QHBoxLayout(container)
        c.setContentsMargins(2, 2, 2, 2)
        c.setSpacing(2)

        self.buttons: list[QPushButton] = []
        for i, text in enumerate(labels):
            b = QPushButton(text)
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.setMinimumHeight(28)
            b.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: rgba(245,245,255,0.70);
                    padding: 6px 12px;
                    border-radius: 12px;
                    font-size: 12px;
                }
                QPushButton:checked {
                    background: rgba(220, 210, 255, 0.90);
                    color: rgba(30, 25, 45, 1.0);
                }
            """)
            self.group.addButton(b, i)
            self.buttons.append(b)
            c.addWidget(b)

        self.group.idClicked.connect(self.changed.emit)
        root.addWidget(container)
        container.setFixedWidth(fixed_width)
        if self.buttons:
            self.buttons[0].setChecked(True)

    def current_index(self) -> int:
        return self.group.checkedId()