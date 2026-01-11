# UI/Views/GameScreen.py
from typing import Optional, List, Callable, Dict, Any
from datetime import datetime
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox
)
from ApplicationControl.IBoundary import IBoundary
from UI.Components.BoardWidget import BoardWidget
from UI.Components.InputBar import InputBar
from UI.Components.FeedbackInput import FeedbackInput
from UI.Components.SecretCodeDisplay import SecretCodeDisplay
from UI.Threads.GameThread import GameThread
from UI.Utils.ColorMapper import (
    PEG_COLOR_MAP, PALETTE_SUPERHIRN, PALETTE_SUPERSUPERHIRN, color_to_name
)
from UI.Utils.SettingsManager import SettingsManager, GameHistoryEntry


def make_card() -> QFrame:
    f = QFrame()
    f.setObjectName("Card")
    return f


class GameScreen(QWidget):
    """Game screen driven by IBoundary callbacks."""

    def __init__(self, boundary: IBoundary, parent=None):
        super().__init__(parent)
        self.boundary = boundary
        self.boundary.set_on_round_played(self._on_round_played)
        self.boundary.set_on_game_won(self._on_game_won)
        self.boundary.set_on_game_lost(self._on_game_lost)
        self.boundary.set_on_computer_guess(self._on_computer_guess)
        self.boundary.set_on_waiting_for_feedback(self._on_waiting_for_feedback)

        self.config: Dict[str, Any] = {}
        self.variant_name: Optional[str] = None
        self.mode: Optional[str] = None
        self.code_length: int = 4
        self.game_thread: Optional[GameThread] = None
        self.current_round = 0
        self.current_round1 = 0
        self.current_round2 = 0
        self.last_computer_guess_colors: Optional[List[QColor]] = None
        self.secret_code_colors: Optional[List[QColor]] = None
        self.kodierer_mode: Optional[str] = None
        self._on_back_callback: Optional[Callable] = None
        self.spectator_timer: Optional[QTimer] = None

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        top = QHBoxLayout()
        self.back_btn = QPushButton("← Settings")
        self.back_btn.setObjectName("Ghost")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.clicked.connect(self._on_back)
        top.addWidget(self.back_btn, alignment=Qt.AlignLeft)
        top.addStretch(1)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: rgba(245,245,255,0.8); font-size: 14px;")
        top.addWidget(self.status_label, alignment=Qt.AlignRight)

        self.step_btn = QPushButton("Nächster Schritt")
        self.step_btn.setObjectName("Ghost")
        self.step_btn.setCursor(Qt.PointingHandCursor)
        self.step_btn.clicked.connect(self._on_step_clicked)
        self.step_btn.hide()
        top.addWidget(self.step_btn, alignment=Qt.AlignRight)
        root.addLayout(top)

        self.boards_card = make_card()
        root.addWidget(self.boards_card, stretch=1)
        self.boards_layout = QHBoxLayout(self.boards_card)
        self.boards_layout.setContentsMargins(18, 18, 18, 18)
        self.boards_layout.setSpacing(18)

        self.board_widget: Optional[BoardWidget] = None
        self.board_widget1: Optional[BoardWidget] = None
        self.board_widget2: Optional[BoardWidget] = None

        self.input_bar: Optional[InputBar] = None
        self.feedback_input: Optional[FeedbackInput] = None
        self.secret_code_display: Optional[SecretCodeDisplay] = None

        self.new_game_container = QFrame()
        self.new_game_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2a2a3d, stop:1 #14141c);
                border: 2px solid rgba(170, 150, 255, 0.7);
                border-radius: 18px;
                padding: 10px;
            }
        """)
        self.new_game_container.hide()
        new_game_layout = QHBoxLayout(self.new_game_container)
        new_game_layout.setContentsMargins(0, 10, 0, 0)
        new_game_layout.addStretch()

        self.new_game_btn = QPushButton("✨ Neues Spiel")
        self.new_game_btn.setObjectName("Primary")
        self.new_game_btn.setCursor(Qt.PointingHandCursor)
        self.new_game_btn.setFixedWidth(280)
        self.new_game_btn.setFixedHeight(56)
        self.new_game_btn.setStyleSheet("""
            QPushButton#Primary {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #a080ff, stop:1 #c0a0ff);
                color: #14141c;
                border: none;
                padding: 12px 24px;
                border-radius: 28px;
                font-size: 20px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            QPushButton#Primary:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #b090ff, stop:1 #d0b0ff);
            }
            QPushButton#Primary:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9070ee, stop:1 #b090ee);
            }
        """)
        self.new_game_btn.clicked.connect(self._on_new_game_clicked)
        new_game_layout.addWidget(self.new_game_btn)
        new_game_layout.addStretch()

        root.addWidget(self.new_game_container)
        root.addStretch()

    def _on_back(self):
        if self._on_back_callback:
            self._on_back_callback()

    def set_on_back_callback(self, callback: Callable[[], None]):
        self._on_back_callback = callback

    def get_widget(self):
        return self

    def initialize_game(self, config: Dict[str, Any]) -> bool:
        self.config = config
        self.mode = config.get("mode", "RATER")
        self.kodierer_mode = config.get("kodierer_mode", "Mensch")
        self.variant_name = config.get("variant", "SUPERHIRN")
        self.code_length = 4 if self.variant_name == "SUPERHIRN" else 5
        self.current_round = 0
        self.current_round1 = 0
        self.current_round2 = 0
        self.last_computer_guess_colors = None
        self.secret_code_colors = None
        self.new_game_container.hide()
        self.step_btn.hide()
        if self.spectator_timer:
            self.spectator_timer.stop()
            self.spectator_timer = None

        self._clear_widgets()

        palette = PALETTE_SUPERHIRN if self.variant_name == "SUPERHIRN" else PALETTE_SUPERSUPERHIRN
        if self.mode == "ZUSCHAUER":
            self._create_dual_boards(palette)
        else:
            self._create_single_board(palette)

        if self.mode in ("RATER", "KODIERER"):
            self._create_input_bar(palette)
        if self.mode == "KODIERER":
            self._create_feedback_input()
            self.feedback_input.hide()

        success = self.boundary.start_new_game(config)
        if not success:
            error = self.boundary.get_game_view().get("error", "Unbekannter Fehler")
            QMessageBox.warning(self, "Connection Failed", error)
            return False

        if self.mode == "ZUSCHAUER":
            self.step_btn.show()
            self._start_spectator_timer()
            self.update_status("Zuschauer-Modus läuft...")
        elif self.mode == "KODIERER" and self.kodierer_mode != "Mensch":
            self._start_game_thread()
            self.update_status("Spiel läuft...")
        elif self.mode == "RATER":
            self.update_status("Dein Zug...")
        else:
            self.update_status("Bereit für Feedback...")
        return True

    def _clear_widgets(self):
        if self.secret_code_display:
            self.secret_code_display.setParent(None)
            self.secret_code_display.deleteLater()
            self.secret_code_display = None
        if self.input_bar:
            self.input_bar.setParent(None)
            self.input_bar.deleteLater()
            self.input_bar = None
        if self.feedback_input:
            self.feedback_input.setParent(None)
            self.feedback_input.deleteLater()
            self.feedback_input = None

        while self.boards_layout.count():
            item = self.boards_layout.takeAt(0)
            if item and item.widget():
                item.widget().setParent(None)
                item.widget().deleteLater()

    def _create_single_board(self, palette: List[QColor]):
        self.board_widget = BoardWidget(self.code_length, "")
        self.boards_layout.addWidget(self.board_widget)

    def _create_dual_boards(self, palette: List[QColor]):
        algorithm1 = self.config.get("algorithm1", "Consistency")
        algorithm2 = self.config.get("algorithm2", "Consistency")
        self.board_widget1 = BoardWidget(self.code_length, f"Board 1: {algorithm1}")
        self.board_widget2 = BoardWidget(self.code_length, f"Board 2: {algorithm2}")
        self.boards_layout.addWidget(self.board_widget1)
        self.boards_layout.addWidget(self.board_widget2)

    def _create_input_bar(self, palette: List[QColor]):
        self.input_bar = InputBar(self.code_length, palette)
        self.input_bar.submitted.connect(self._on_input_submitted)
        self.layout().insertWidget(1, self.input_bar)

    def _create_feedback_input(self):
        self.feedback_input = FeedbackInput(self.code_length)
        self.feedback_input.submitted.connect(self._on_feedback_submitted)
        self.layout().insertWidget(1, self.feedback_input)

    def _on_input_submitted(self, colors: List[QColor]):
        if self.mode == "KODIERER":
            if self.current_round == 0 and self.secret_code_colors is None:
                self._on_secret_code_submitted(colors)
        elif self.mode == "RATER":
            self._on_guess_submitted(colors)

    def _on_guess_submitted(self, colors: List[QColor]):
        color_names = [color_to_name(c) for c in colors]
        self.boundary.submit_guess(color_names)
        if self.input_bar:
            self.input_bar.set_enabled(False)
        self.update_status("Warte auf Feedback...")

    def _on_secret_code_submitted(self, colors: List[QColor]):
        if len(colors) != self.code_length:
            QMessageBox.warning(self, "Ungültiger Code",
                                f"Der Code muss {self.code_length} Farben haben!")
            return
        self.secret_code_colors = colors
        self._show_secret_code_display(colors)
        color_names = [color_to_name(c) for c in colors]
        self.boundary.submit_secret_code(color_names)
        if self.input_bar:
            self.input_bar.hide()
        if self.feedback_input:
            self.feedback_input.show()

    def _show_secret_code_display(self, colors: List[QColor]):
        if self.secret_code_display:
            self.secret_code_display.setParent(None)
            self.secret_code_display.deleteLater()
        self.secret_code_display = SecretCodeDisplay()
        self.secret_code_display.display_code(colors)
        self.layout().insertWidget(2, self.secret_code_display)

    def _on_feedback_submitted(self, black: int, white: int):
        max_pegs = self.code_length
        if black + white > max_pegs:
            QMessageBox.warning(self, "Ungültiges Feedback",
                                f"Schwarz + Weiß darf nicht größer als {max_pegs} sein!")
            return

        if not self.last_computer_guess_colors:
            return

        if self.board_widget and self.current_round < len(self.board_widget.rows):
            row = self.board_widget.rows[self.current_round]
            row.set_feedback(black, white)
            self.board_widget.update()
            self.current_round += 1

        self.boundary.submit_feedback(black, white)
        if self.feedback_input:
            self.feedback_input.reset()
            self.feedback_input.hide()
        self.update_status("Warte auf nächsten Zug des Computers...")
        self.last_computer_guess_colors = None

    def _start_game_thread(self):
        self.game_thread = GameThread(self.boundary, self)
        self.game_thread.finished.connect(lambda: self._on_game_finished())
        self.game_thread.error.connect(self._on_game_error)
        self.game_thread.start()

    def _start_spectator_timer(self):
        delay_seconds = self.config.get("delay", 1)
        if delay_seconds <= 0:
            return
        self.spectator_timer = QTimer(self)
        self.spectator_timer.timeout.connect(self._on_step_clicked)
        self.spectator_timer.start(int(delay_seconds * 1000))

    def _on_step_clicked(self):
        self.boundary.step()

    def _on_round_played(self, payload: Dict[str, Any]):
        if self.mode == "KODIERER" and self.kodierer_mode == "Mensch":
            return
        QTimer.singleShot(0, lambda p=payload: self._update_round_ui(p))

    def _update_round_ui(self, payload: Dict[str, Any]):
        board = payload.get("board", 0)
        guess_names = payload.get("guess", [])
        feedback = payload.get("feedback", {})
        guess_colors = [PEG_COLOR_MAP.get(name, QColor("#ffffff")) for name in guess_names]
        black = feedback.get("black", 0)
        white = feedback.get("white", 0)

        if self.mode == "ZUSCHAUER":
            if board == 1 and self.board_widget1:
                self.board_widget1.add_round(guess_colors, black, white)
                self.current_round1 += 1
            elif board == 2 and self.board_widget2:
                self.board_widget2.add_round(guess_colors, black, white)
                self.current_round2 += 1
            self.update_status(f"Board 1: {self.current_round1} Runden | Board 2: {self.current_round2} Runden")
        else:
            if not self.board_widget:
                return
            self.board_widget.add_round(guess_colors, black, white)
            self.current_round += 1
            self.board_widget.update()

            if self.mode == "RATER" and self.input_bar:
                self.input_bar.set_enabled(True)
                self.update_status("Dein Zug...")
            elif self.mode == "KODIERER":
                self.update_status(f"Runde {self.current_round}: Computer rät weiter...")

    def _on_computer_guess(self, payload: Dict[str, Any]):
        QTimer.singleShot(0, lambda p=payload: self._show_computer_guess(p))

    def _on_waiting_for_feedback(self, payload: Dict[str, Any]):
        QTimer.singleShot(0, self._show_feedback_prompt)

    def _show_computer_guess(self, payload: Dict[str, Any]):
        guess_names = payload.get("guess", [])
        guess_colors = [PEG_COLOR_MAP.get(name, QColor("#ffffff")) for name in guess_names]
        self.last_computer_guess_colors = guess_colors
        if self.board_widget and self.current_round < len(self.board_widget.rows):
            row = self.board_widget.rows[self.current_round]
            row.set_guess(guess_colors)
            self.board_widget.update()

    def _show_feedback_prompt(self):
        if self.feedback_input:
            self.feedback_input.show()
            self.update_status("Computer hat geraten. Gib Feedback...")

    def _on_game_won(self, payload: Dict[str, Any]):
        board = payload.get("board", 0)
        rounds = payload.get("rounds", 0)
        if self.spectator_timer:
            self.spectator_timer.stop()
        self.show_game_won(rounds, board)

    def _on_game_lost(self, payload: Dict[str, Any]):
        board = payload.get("board", 0)
        rounds = payload.get("rounds", 0)
        if self.spectator_timer:
            self.spectator_timer.stop()
        self.show_game_lost(rounds, board)

    def show_game_won(self, rounds: int, board: int = 0):
        QTimer.singleShot(0, lambda r=rounds, b=board: self._show_win(r, b))

    def _show_win(self, rounds: int, board: int = 0):
        view = self.boundary.get_game_view()
        if self.mode == "ZUSCHAUER":
            boards = view.get("boards", [])
            if len(boards) >= 2:
                rounds1 = len(boards[0]["rounds"])
                rounds2 = len(boards[1]["rounds"])
                state1 = boards[0]["state"]
                state2 = boards[1]["state"]
                board1_result = "gewonnen" if state1 == "WON" else "verloren"
                board2_result = "gewonnen" if state2 == "WON" else "verloren"
                if rounds1 < rounds2:
                    faster_text = "Board 1 war schneller"
                elif rounds2 < rounds1:
                    faster_text = "Board 2 war schneller"
                else:
                    faster_text = "Beide Boards gleich schnell"
                result_text = (
                    f"Board 1 hat mit {rounds1} Runden {board1_result} || "
                    f"Board 2 hat mit {rounds2} Runden {board2_result}"
                )
                self.update_status(result_text)
                msg = QMessageBox(self)
                msg.setWindowTitle("Spiele beendet")
                msg.setText(f"<div style='font-size: 16px; padding: 15px; line-height: 1.8;'>"
                            f"<p style='margin: 8px 0; color: #a080ff; font-weight: bold;'>Board 1: {rounds1} Runden - {board1_result.capitalize()}</p>"
                            f"<p style='margin: 8px 0; color: #a080ff; font-weight: bold;'>Board 2: {rounds2} Runden - {board2_result.capitalize()}</p>"
                            f"<p style='margin: 8px 0; color: #fdd835; font-weight: bold; font-size: 18px;'>{faster_text}</p>"
                            f"</div>")
                msg.setIcon(QMessageBox.NoIcon)
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #1a1a2e;
                        color: #f5f5ff;
                    }
                    QMessageBox QLabel {
                        color: #f5f5ff;
                        background-color: transparent;
                    }
                    QPushButton {
                        background-color: #a080ff;
                        color: #14141c;
                        border: none;
                        padding: 8px 20px;
                        border-radius: 8px;
                        font-weight: bold;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #b090ff;
                    }
                """)
                msg.buttonClicked.connect(self._on_game_end_message_closed)
                msg.exec()
                self._show_new_game_button()
            return

        self.update_status("Gewonnen")
        stats = SettingsManager.load_stats()
        stats.games_played += 1
        stats.games_won += 1
        stats.total_rounds += rounds
        if rounds < stats.best_score:
            stats.best_score = rounds
        SettingsManager.save_stats(stats)

        SettingsManager.add_history_entry(GameHistoryEntry(
            mode=self.mode,
            variant=self.variant_name or "",
            won=True,
            rounds=rounds,
            timestamp=datetime.now().isoformat()
        ))

        msg = QMessageBox(self)
        msg.setWindowTitle("Gewonnen!")
        msg.setText(f"<div style='font-size: 16px; padding: 10px;'>"
                    f"<p style='margin: 5px 0;'><b>🎉 Du hast in {rounds} Runden gewonnen!</b></p>"
                    f"</div>")
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1a1a2e;
                color: #f5f5ff;
            }
            QMessageBox QLabel {
                color: #f5f5ff;
                background-color: transparent;
            }
            QPushButton {
                background-color: #a080ff;
                color: #14141c;
                border: none;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #b090ff;
            }
        """)
        msg.buttonClicked.connect(self._on_game_end_message_closed)
        msg.exec()
        self._show_new_game_button()

    def show_game_lost(self, rounds: int, board: int = 0):
        QTimer.singleShot(0, lambda r=rounds, b=board: self._show_loss(r, b))

    def _show_loss(self, rounds: int, board: int = 0):
        view = self.boundary.get_game_view()
        if self.mode == "ZUSCHAUER":
            boards = view.get("boards", [])
            if len(boards) >= 2:
                rounds1 = len(boards[0]["rounds"])
                rounds2 = len(boards[1]["rounds"])
                state1 = boards[0]["state"]
                state2 = boards[1]["state"]
                board1_result = "gewonnen" if state1 == "WON" else "verloren"
                board2_result = "gewonnen" if state2 == "WON" else "verloren"
                if rounds1 < rounds2:
                    faster_text = "Board 1 war schneller"
                elif rounds2 < rounds1:
                    faster_text = "Board 2 war schneller"
                else:
                    faster_text = "Beide Boards gleich schnell"
                result_text = (
                    f"Board 1 hat mit {rounds1} Runden {board1_result} || "
                    f"Board 2 hat mit {rounds2} Runden {board2_result}"
                )
                self.update_status(result_text)
                secret_code = boards[0].get("secret_code")
                if board1_result == "verloren" and board2_result == "verloren" and secret_code:
                    colors = [PEG_COLOR_MAP.get(name, QColor("#ffffff")) for name in secret_code]
                    self._show_secret_code_display(colors)
                msg = QMessageBox(self)
                msg.setWindowTitle("Spiele beendet")
                msg.setText(f"<div style='font-size: 16px; padding: 15px; line-height: 1.8;'>"
                            f"<p style='margin: 8px 0; color: #a080ff; font-weight: bold;'>Board 1: {rounds1} Runden - {board1_result.capitalize()}</p>"
                            f"<p style='margin: 8px 0; color: #a080ff; font-weight: bold;'>Board 2: {rounds2} Runden - {board2_result.capitalize()}</p>"
                            f"<p style='margin: 8px 0; color: #fdd835; font-weight: bold; font-size: 18px;'>{faster_text}</p>"
                            f"</div>")
                msg.setIcon(QMessageBox.NoIcon)
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #1a1a2e;
                        color: #f5f5ff;
                    }
                    QMessageBox QLabel {
                        color: #f5f5ff;
                        background-color: transparent;
                    }
                    QPushButton {
                        background-color: #a080ff;
                        color: #14141c;
                        border: none;
                        padding: 8px 20px;
                        border-radius: 8px;
                        font-weight: bold;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #b090ff;
                    }
                """)
                msg.buttonClicked.connect(self._on_game_end_message_closed)
                msg.exec()
                self._show_new_game_button()
            return

        self.update_status("Verloren")
        stats = SettingsManager.load_stats()
        stats.games_played += 1
        stats.total_rounds += rounds
        SettingsManager.save_stats(stats)

        SettingsManager.add_history_entry(GameHistoryEntry(
            mode=self.mode,
            variant=self.variant_name or "",
            won=False,
            rounds=rounds,
            timestamp=datetime.now().isoformat()
        ))

        boards = view.get("boards", [])
        if boards:
            secret_code = boards[0].get("secret_code")
            if secret_code:
                colors = [PEG_COLOR_MAP.get(name, QColor("#ffffff")) for name in secret_code]
                self._show_secret_code_display(colors)

        msg = QMessageBox(self)
        msg.setWindowTitle("Verloren")
        msg.setText(f"<div style='font-size: 16px; padding: 10px;'>"
                    f"<p style='margin: 5px 0;'><b>❌ Du hast alle Versuche aufgebraucht.</b></p>"
                    f"</div>")
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1a1a2e;
                color: #f5f5ff;
            }
            QMessageBox QLabel {
                color: #f5f5ff;
                background-color: transparent;
            }
            QPushButton {
                background-color: #a080ff;
                color: #14141c;
                border: none;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #b090ff;
            }
        """)
        msg.buttonClicked.connect(self._on_game_end_message_closed)
        msg.exec()
        self._show_new_game_button()

    def _show_new_game_button(self):
        if self.new_game_container:
            self.new_game_container.show()
        if self.step_btn:
            self.step_btn.hide()

    def _on_game_end_message_closed(self, button):
        self._show_new_game_button()

    def _on_new_game_clicked(self):
        if self.new_game_container:
            self.new_game_container.hide()
        if self.spectator_timer:
            self.spectator_timer.stop()
            self.spectator_timer = None
        if self._on_back_callback:
            self._on_back_callback()

    def _on_game_finished(self):
        self.update_status("Spiel beendet")

    def _on_game_error(self, error_msg: str):
        if self.spectator_timer:
            self.spectator_timer.stop()
        QMessageBox.critical(self, "Fehler", f"Spiel-Fehler: {error_msg}")
        self.update_status("Fehler aufgetreten")

    def update_status(self, message: str):
        self.status_label.setText(message)
