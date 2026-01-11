# UI/Views/SettingsView.py
from typing import Callable
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSpacerItem, QFrame, QSpinBox, QMessageBox, QCheckBox, QLineEdit
)
from CoreDomainModel.GameVariant import GameVariant
from UI.IBoundary import ISettingsView
from UI.Components.Segmented import Segmented
from UI.Utils.SettingsManager import SettingsManager


def make_card() -> QFrame:
    f = QFrame()
    f.setObjectName("Card")
    return f


class SettingsView(QWidget):
    """Settings view - implements ISettingsView interface"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._on_start_callback: Callable = None

        # Load saved settings
        settings = SettingsManager.load_settings()

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(0)

        card = make_card()
        root.addWidget(card)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(70, 60, 70, 60)
        lay.setSpacing(18)

        title = QLabel("THE\nMASTERMIND\nGAME")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignHCenter)
        lay.addWidget(title)

        lay.addSpacing(10)

        # Variant selection
        self.variant_seg = Segmented([" Superhirn", "Super-Superhirn"], fixed_width=520)
        if settings.get("default_variant") == "SUPERSUPERHIRN":
            self.variant_seg.buttons[1].setChecked(True)
        lay.addWidget(self.variant_seg, alignment=Qt.AlignHCenter)

        # Mode selection
        self.mode_seg = Segmented(["Rater", "Kodierer", "Zuschauer"], fixed_width=520)
        mode_map = {"RATER": 0, "KODIERER": 1, "ZUSCHAUER": 2}
        default_mode_idx = mode_map.get(settings.get("default_mode", "RATER"), 0)
        self.mode_seg.buttons[default_mode_idx].setChecked(True)
        self.mode_seg.changed.connect(self.on_mode_changed)
        lay.addWidget(self.mode_seg, alignment=Qt.AlignHCenter)

        # RATER Mode selection (Local/Online)
        self.rater_mode_label = QLabel("Rater-Modus:")
        self.rater_mode_label.setStyleSheet("color: rgba(245,245,255,0.8); font-size: 14px;")
        self.rater_mode_label.setAlignment(Qt.AlignHCenter)
        self.rater_mode_label.setVisible(False)
        lay.addWidget(self.rater_mode_label, alignment=Qt.AlignHCenter)

        self.rater_mode_seg = Segmented(["Local", "Online"], fixed_width=300)
        self.rater_mode_seg.setVisible(False)
        self.rater_mode_seg.changed.connect(self.on_rater_mode_changed)
        lay.addWidget(self.rater_mode_seg, alignment=Qt.AlignHCenter)

        # Server IP
        self.server_ip_label = QLabel("Server IP:")
        self.server_ip_label.setStyleSheet("color: rgba(245,245,255,0.8); font-size: 12px;")
        self.server_ip_label.setAlignment(Qt.AlignHCenter)
        self.server_ip_label.setVisible(False)
        lay.addWidget(self.server_ip_label, alignment=Qt.AlignHCenter)

        self.server_ip_edit = QLineEdit()
        self.server_ip_edit.setPlaceholderText("127.0.0.1")
        self.server_ip_edit.setText(settings.get("default_server_ip", "127.0.0.1"))
        self.server_ip_edit.setVisible(False)
        self.server_ip_edit.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
                padding: 6px;
                color: rgba(245,245,255,0.9);
                font-size: 14px;
                min-width: 200px;
            }
        """)
        lay.addWidget(self.server_ip_edit, alignment=Qt.AlignHCenter)

        # Server Port
        self.server_port_label = QLabel("Server Port:")
        self.server_port_label.setStyleSheet("color: rgba(245,245,255,0.8); font-size: 12px;")
        self.server_port_label.setAlignment(Qt.AlignHCenter)
        self.server_port_label.setVisible(False)
        lay.addWidget(self.server_port_label, alignment=Qt.AlignHCenter)

        self.server_port_spin = QSpinBox()
        self.server_port_spin.setMinimum(1)
        self.server_port_spin.setMaximum(65535)
        self.server_port_spin.setValue(settings.get("default_server_port", 8080))
        self.server_port_spin.setVisible(False)
        self.server_port_spin.setStyleSheet("""
            QSpinBox {
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
                padding: 6px;
                color: rgba(245,245,255,0.9);
                font-size: 14px;
            }
        """)
        lay.addWidget(self.server_port_spin, alignment=Qt.AlignHCenter)

        # Gamer ID
        self.gamer_id_label = QLabel("Gamer ID:")
        self.gamer_id_label.setStyleSheet("color: rgba(245,245,255,0.8); font-size: 12px;")
        self.gamer_id_label.setAlignment(Qt.AlignHCenter)
        self.gamer_id_label.setVisible(False)
        lay.addWidget(self.gamer_id_label, alignment=Qt.AlignHCenter)

        self.gamer_id_edit = QLineEdit()
        self.gamer_id_edit.setPlaceholderText("player1")
        self.gamer_id_edit.setText(settings.get("default_gamer_id", "player1"))
        self.gamer_id_edit.setVisible(False)
        self.gamer_id_edit.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
                padding: 6px;
                color: rgba(245,245,255,0.9);
                font-size: 14px;
                min-width: 200px;
            }
        """)
        lay.addWidget(self.gamer_id_edit, alignment=Qt.AlignHCenter)

        # KODIERER Mode selection (Codierer type)
        self.kodierer_mode_label = QLabel("Codierer:")
        self.kodierer_mode_label.setStyleSheet("color: rgba(245,245,255,0.8); font-size: 14px;")
        self.kodierer_mode_label.setAlignment(Qt.AlignHCenter)
        self.kodierer_mode_label.setVisible(False)
        lay.addWidget(self.kodierer_mode_label, alignment=Qt.AlignHCenter)

        self.kodierer_mode_seg = Segmented(["Mensch", "lokaler Computer", "Codierer im Netz"], fixed_width=500)
        kodierer_mode_map = {"Mensch": 0, "lokaler Computer": 1, "Codierer im Netz": 2}
        default_kodierer_mode_idx = kodierer_mode_map.get(settings.get("default_kodierer_mode", "Mensch"), 0)
        self.kodierer_mode_seg.buttons[default_kodierer_mode_idx].setChecked(True)
        self.kodierer_mode_seg.setVisible(False)
        self.kodierer_mode_seg.changed.connect(self.on_kodierer_mode_changed)
        lay.addWidget(self.kodierer_mode_seg, alignment=Qt.AlignHCenter)

        # KODIERER Server fields (for Codierer im Netz)
        self.kodierer_server_ip_label = QLabel("Codierer Server IP:")
        self.kodierer_server_ip_label.setStyleSheet("color: rgba(245,245,255,0.8); font-size: 12px;")
        self.kodierer_server_ip_label.setAlignment(Qt.AlignHCenter)
        self.kodierer_server_ip_label.setVisible(False)
        lay.addWidget(self.kodierer_server_ip_label, alignment=Qt.AlignHCenter)

        self.kodierer_server_ip_edit = QLineEdit()
        self.kodierer_server_ip_edit.setPlaceholderText("127.0.0.1")
        self.kodierer_server_ip_edit.setText(settings.get("default_kodierer_server_ip", "127.0.0.1"))
        self.kodierer_server_ip_edit.setVisible(False)
        self.kodierer_server_ip_edit.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
                padding: 6px;
                color: rgba(245,245,255,0.9);
                font-size: 14px;
                min-width: 200px;
            }
        """)
        lay.addWidget(self.kodierer_server_ip_edit, alignment=Qt.AlignHCenter)

        self.kodierer_server_port_label = QLabel("Codierer Server Port:")
        self.kodierer_server_port_label.setStyleSheet("color: rgba(245,245,255,0.8); font-size: 12px;")
        self.kodierer_server_port_label.setAlignment(Qt.AlignHCenter)
        self.kodierer_server_port_label.setVisible(False)
        lay.addWidget(self.kodierer_server_port_label, alignment=Qt.AlignHCenter)

        self.kodierer_server_port_spin = QSpinBox()
        self.kodierer_server_port_spin.setMinimum(1)
        self.kodierer_server_port_spin.setMaximum(65535)
        self.kodierer_server_port_spin.setValue(settings.get("default_kodierer_server_port", 8080))
        self.kodierer_server_port_spin.setVisible(False)
        self.kodierer_server_port_spin.setStyleSheet("""
            QSpinBox {
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
                padding: 6px;
                color: rgba(245,245,255,0.9);
                font-size: 14px;
            }
        """)
        lay.addWidget(self.kodierer_server_port_spin, alignment=Qt.AlignHCenter)

        self.kodierer_gamer_id_label = QLabel("Codierer Gamer ID:")
        self.kodierer_gamer_id_label.setStyleSheet("color: rgba(245,245,255,0.8); font-size: 12px;")
        self.kodierer_gamer_id_label.setAlignment(Qt.AlignHCenter)
        self.kodierer_gamer_id_label.setVisible(False)
        lay.addWidget(self.kodierer_gamer_id_label, alignment=Qt.AlignHCenter)

        self.kodierer_gamer_id_edit = QLineEdit()
        self.kodierer_gamer_id_edit.setPlaceholderText("player1")
        self.kodierer_gamer_id_edit.setText(settings.get("default_kodierer_gamer_id", "player1"))
        self.kodierer_gamer_id_edit.setVisible(False)
        self.kodierer_gamer_id_edit.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
                padding: 6px;
                color: rgba(245,245,255,0.9);
                font-size: 14px;
                min-width: 200px;
            }
        """)
        lay.addWidget(self.kodierer_gamer_id_edit, alignment=Qt.AlignHCenter)

        # Algorithm selection for single mode (Kodierer)
        self.algorithm_label = QLabel("Algorithmus:")
        self.algorithm_label.setStyleSheet("color: rgba(245,245,255,0.8); font-size: 14px;")
        self.algorithm_label.setAlignment(Qt.AlignHCenter)
        lay.addWidget(self.algorithm_label, alignment=Qt.AlignHCenter)

        self.algorithm_seg = Segmented(["Consistency", "Knuth"], fixed_width=300)
        algorithm_map = {"Consistency": 0, "Knuth": 1}
        default_algorithm_idx = algorithm_map.get(settings.get("default_algorithm", "Consistency"), 0)
        self.algorithm_seg.buttons[default_algorithm_idx].setChecked(True)
        lay.addWidget(self.algorithm_seg, alignment=Qt.AlignHCenter)

        # Two algorithm selections for Zuschauer mode
        self.zuschauer_label = QLabel("Zuschauer-Modus: Wähle Algorithmen für beide Boards")
        self.zuschauer_label.setStyleSheet("color: rgba(245,245,255,0.8); font-size: 14px; font-weight: bold;")
        self.zuschauer_label.setAlignment(Qt.AlignHCenter)
        lay.addWidget(self.zuschauer_label, alignment=Qt.AlignHCenter)

        # Board 1 algorithm
        self.board1_label = QLabel("Board 1 Algorithmus:")
        self.board1_label.setStyleSheet("color: rgba(245,245,255,0.8); font-size: 12px;")
        self.board1_label.setAlignment(Qt.AlignHCenter)
        lay.addWidget(self.board1_label, alignment=Qt.AlignHCenter)

        self.algorithm1_seg = Segmented(["Consistency", "Knuth"], fixed_width=300)
        algorithm1_map = {"Consistency": 0, "Knuth": 1}
        default_algorithm1_idx = algorithm1_map.get(settings.get("default_algorithm1", "Consistency"), 0)
        self.algorithm1_seg.buttons[default_algorithm1_idx].setChecked(True)
        lay.addWidget(self.algorithm1_seg, alignment=Qt.AlignHCenter)

        # Board 2 algorithm
        self.board2_label = QLabel("Board 2 Algorithmus:")
        self.board2_label.setStyleSheet("color: rgba(245,245,255,0.8); font-size: 12px;")
        self.board2_label.setAlignment(Qt.AlignHCenter)
        lay.addWidget(self.board2_label, alignment=Qt.AlignHCenter)

        self.algorithm2_seg = Segmented(["Consistency", "Knuth"], fixed_width=300)
        algorithm2_map = {"Consistency": 0, "Knuth": 1}
        default_algorithm2_idx = algorithm2_map.get(settings.get("default_algorithm2", "Consistency"), 0)
        self.algorithm2_seg.buttons[default_algorithm2_idx].setChecked(True)
        lay.addWidget(self.algorithm2_seg, alignment=Qt.AlignHCenter)

        # Timer/Delay selection for Zuschauer
        self.timer_label = QLabel("Verzögerung zwischen Zügen (Sekunden):")
        self.timer_label.setStyleSheet("color: rgba(245,245,255,0.8); font-size: 12px;")
        self.timer_label.setAlignment(Qt.AlignHCenter)
        lay.addWidget(self.timer_label, alignment=Qt.AlignHCenter)

        self.delay_spin = QSpinBox()
        self.delay_spin.setMinimum(0)
        self.delay_spin.setMaximum(10)
        self.delay_spin.setValue(settings.get("default_delay", 1))
        self.delay_spin.setStyleSheet("""
            QSpinBox {
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
                padding: 6px;
                color: rgba(245,245,255,0.9);
                font-size: 14px;
            }
        """)
        lay.addWidget(self.delay_spin, alignment=Qt.AlignHCenter)

        # Initially hide/show based on mode
        self.on_mode_changed(self.mode_seg.current_index())

        lay.addItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Statistics button
        stats_btn = QPushButton("📊 Statistiken")
        stats_btn.setObjectName("Ghost")
        stats_btn.setCursor(Qt.PointingHandCursor)
        stats_btn.clicked.connect(self.show_statistics)
        lay.addWidget(stats_btn, alignment=Qt.AlignHCenter)

        # Start game
        start = QPushButton("Spiel starten")
        start.setObjectName("Primary")
        start.setCursor(Qt.PointingHandCursor)
        start.setFixedWidth(220)
        start.setFixedHeight(44)
        start.clicked.connect(self.on_start_clicked)
        lay.addWidget(start, alignment=Qt.AlignHCenter)

    def on_mode_changed(self, mode_index: int):
        """Show/hide options based on selected mode"""
        is_rater = (mode_index == 0)  # RATER

        self.rater_mode_label.setVisible(is_rater)
        self.rater_mode_seg.setVisible(is_rater)

        if is_rater:
            self.on_rater_mode_changed(self.rater_mode_seg.current_index())
        else:
            self.server_ip_label.setVisible(False)
            self.server_ip_edit.setVisible(False)
            self.server_port_label.setVisible(False)
            self.server_port_spin.setVisible(False)
            self.gamer_id_label.setVisible(False)
            self.gamer_id_edit.setVisible(False)

        is_kodierer = (mode_index == 1)  # Kodierer
        self.kodierer_mode_label.setVisible(is_kodierer)
        self.kodierer_mode_seg.setVisible(is_kodierer)

        if is_kodierer:
            self.on_kodierer_mode_changed(self.kodierer_mode_seg.current_index())
        else:
            self.kodierer_server_ip_label.setVisible(False)
            self.kodierer_server_ip_edit.setVisible(False)
            self.kodierer_server_port_label.setVisible(False)
            self.kodierer_server_port_spin.setVisible(False)
            self.kodierer_gamer_id_label.setVisible(False)
            self.kodierer_gamer_id_edit.setVisible(False)

        show_single = (mode_index == 1)  # Kodierer
        self.algorithm_label.setVisible(show_single)
        self.algorithm_seg.setVisible(show_single)

        show_double = (mode_index == 2)  # Zuschauer
        self.zuschauer_label.setVisible(show_double)
        self.board1_label.setVisible(show_double)
        self.algorithm1_seg.setVisible(show_double)
        self.board2_label.setVisible(show_double)
        self.algorithm2_seg.setVisible(show_double)
        self.timer_label.setVisible(show_double)
        self.delay_spin.setVisible(show_double)

    def on_rater_mode_changed(self, mode_index: int):
        """Show/hide IP/Port/GamerID fields based on Local/Online"""
        is_online = (mode_index == 1)  # Online

        self.server_ip_label.setVisible(is_online)
        self.server_ip_edit.setVisible(is_online)
        self.server_port_label.setVisible(is_online)
        self.server_port_spin.setVisible(is_online)
        self.gamer_id_label.setVisible(is_online)
        self.gamer_id_edit.setVisible(is_online)

    def on_kodierer_mode_changed(self, mode_index: int):
        """Show/hide fields based on Codierer type"""
        is_online_codierer = (mode_index == 2)  # Codierer im Netz

        self.kodierer_server_ip_label.setVisible(is_online_codierer)
        self.kodierer_server_ip_edit.setVisible(is_online_codierer)
        self.kodierer_server_port_label.setVisible(is_online_codierer)
        self.kodierer_server_port_spin.setVisible(is_online_codierer)
        self.kodierer_gamer_id_label.setVisible(is_online_codierer)
        self.kodierer_gamer_id_edit.setVisible(is_online_codierer)

    def on_start_clicked(self):
        # Save settings
        variant_name = "SUPERHIRN" if self.variant_seg.current_index() == 0 else "SUPERSUPERHIRN"
        mode_names = ["RATER", "KODIERER", "ZUSCHAUER"]
        mode_name = mode_names[self.mode_seg.current_index()]

        algorithm_names = ["Consistency", "Knuth"]
        algorithm_name = algorithm_names[self.algorithm_seg.current_index()]
        algorithm1_name = algorithm_names[self.algorithm1_seg.current_index()]
        algorithm2_name = algorithm_names[self.algorithm2_seg.current_index()]

        kodierer_mode_names = ["Mensch", "lokaler Computer", "Codierer im Netz"]
        kodierer_mode_name = kodierer_mode_names[self.kodierer_mode_seg.current_index()] if self.kodierer_mode_seg.isVisible() else "Mensch"

        SettingsManager.save_settings({
            "default_variant": variant_name,
            "default_mode": mode_name,
            "default_algorithm": algorithm_name,
            "default_algorithm1": algorithm1_name,
            "default_algorithm2": algorithm2_name,
            "default_delay": self.delay_spin.value(),
            "default_server_ip": self.server_ip_edit.text().strip(),
            "default_server_port": self.server_port_spin.value(),
            "default_gamer_id": self.gamer_id_edit.text().strip(),
            "default_kodierer_mode": kodierer_mode_name,
            "default_kodierer_server_ip": self.kodierer_server_ip_edit.text().strip(),
            "default_kodierer_server_port": self.kodierer_server_port_spin.value(),
            "default_kodierer_gamer_id": self.kodierer_gamer_id_edit.text().strip()
        })

        if self._on_start_callback:
            self._on_start_callback()

    # ISettingsView interface methods
    def get_variant(self) -> GameVariant:
        return GameVariant.SUPERHIRN if self.variant_seg.current_index() == 0 else GameVariant.SUPERSUPERHIRN

    def get_mode(self) -> str:
        modes = ["RATER", "KODIERER", "ZUSCHAUER"]
        return modes[self.mode_seg.current_index()]

    def get_algorithm(self) -> str:
        algorithms = ["Consistency", "Knuth"]
        return algorithms[self.algorithm_seg.current_index()]

    def get_algorithm1(self) -> str:
        algorithms = ["Consistency", "Knuth"]
        return algorithms[self.algorithm1_seg.current_index()]

    def get_algorithm2(self) -> str:
        algorithms = ["Consistency", "Knuth"]
        return algorithms[self.algorithm2_seg.current_index()]

    def get_delay(self) -> int:
        return self.delay_spin.value()

    def get_rater_mode(self) -> str:
        """Returns 'Local' or 'Online'"""
        if not self.rater_mode_seg.isVisible():
            return "Local"
        modes = ["Local", "Online"]
        return modes[self.rater_mode_seg.current_index()]

    def get_server_ip(self) -> str:
        """Returns IP address"""
        return self.server_ip_edit.text().strip() or "127.0.0.1"

    def get_server_port(self) -> int:
        """Returns port number"""
        return self.server_port_spin.value()

    def get_gamer_id(self) -> str:
        """Returns gamer ID"""
        return self.gamer_id_edit.text().strip() or "player1"

    def get_kodierer_mode(self) -> str:
        """Returns 'Mensch', 'lokaler Computer', or 'Codierer im Netz'"""
        if not self.kodierer_mode_seg.isVisible():
            return "Mensch"
        modes = ["Mensch", "lokaler Computer", "Codierer im Netz"]
        return modes[self.kodierer_mode_seg.current_index()]

    def get_kodierer_server_ip(self) -> str:
        """Returns Codierer server IP address"""
        return self.kodierer_server_ip_edit.text().strip() or "127.0.0.1"

    def get_kodierer_server_port(self) -> int:
        """Returns Codierer server port number"""
        return self.kodierer_server_port_spin.value()

    def get_kodierer_gamer_id(self) -> str:
        """Returns Codierer gamer ID"""
        return self.kodierer_gamer_id_edit.text().strip() or "player1"

    def set_on_start_callback(self, callback: Callable[[], None]):
        self._on_start_callback = callback

    def get_widget(self):
        return self

    def get_use_remote_server(self) -> bool:
        """Get whether remote server is enabled (always False - server removed)"""
        return False

    def get_server_url(self) -> str:
        """Get server URL (always None - server removed)"""
        return None

    def show_statistics(self):
        from UI.Utils.SettingsManager import SettingsManager
        stats = SettingsManager.load_stats()
        msg = QMessageBox(self)
        msg.setWindowTitle("Statistiken")
        msg.setText(f"""
        <h3>Spielstatistiken</h3>
        <p><b>Spiele gespielt:</b> {stats.games_played}</p>
        <p><b>Gewonnen:</b> {stats.games_won}</p>
        <p><b>Gewinnrate:</b> {stats.win_rate:.1f}%</p>
        <p><b>Durchschnittliche Runden:</b> {stats.avg_rounds:.1f}</p>
        <p><b>Bester Score:</b> {stats.best_score if stats.best_score < 999 else 'N/A'}</p>
        """)
        msg.exec()