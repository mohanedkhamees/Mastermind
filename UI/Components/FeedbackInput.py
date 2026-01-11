# UI1/Components/FeedbackInput.py
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSpinBox


class FeedbackInput(QFrame):
    submitted = Signal(int, int)  # black, white

    def __init__(self, max_pegs: int, parent=None):
        super().__init__(parent)
        self.max_pegs = max_pegs

        self.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 18px;
                padding: 14px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(14)

        # Label
        label = QLabel("Computer hat geraten. Gib Feedback:")
        label.setStyleSheet("color: rgba(245,245,255,0.8); font-size: 14px;")
        layout.addWidget(label)

        # Black pegs input
        black_label = QLabel("Schwarz (richtige Position):")
        black_label.setStyleSheet("color: rgba(245,245,255,0.8); font-size: 12px;")
        layout.addWidget(black_label)

        self.black_spin = QSpinBox()
        self.black_spin.setMinimum(0)
        self.black_spin.setMaximum(max_pegs)
        self.black_spin.setValue(0)
        self.black_spin.setStyleSheet("""
            QSpinBox {
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
                padding: 6px;
                color: rgba(245,245,255,0.9);
                font-size: 14px;
            }
        """)
        layout.addWidget(self.black_spin)

        # White pegs input
        white_label = QLabel("Weiß (richtige Farbe):")
        white_label.setStyleSheet("color: rgba(245,245,255,0.8); font-size: 12px;")
        layout.addWidget(white_label)

        self.white_spin = QSpinBox()
        self.white_spin.setMinimum(0)
        self.white_spin.setMaximum(max_pegs)
        self.white_spin.setValue(0)
        self.white_spin.setStyleSheet("""
            QSpinBox {
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
                padding: 6px;
                color: rgba(245,245,255,0.9);
                font-size: 14px;
            }
        """)
        layout.addWidget(self.white_spin)

        # Submit feedback button
        submit_feedback_btn = QPushButton("Feedback geben")
        submit_feedback_btn.setObjectName("Primary")
        submit_feedback_btn.setCursor(Qt.PointingHandCursor)
        submit_feedback_btn.clicked.connect(self.on_submit)
        layout.addWidget(submit_feedback_btn)

        layout.addStretch()

    def on_submit(self):
        black = self.black_spin.value()
        white = self.white_spin.value()
        self.submitted.emit(black, white)

    def reset(self):
        self.black_spin.setValue(0)
        self.white_spin.setValue(0)