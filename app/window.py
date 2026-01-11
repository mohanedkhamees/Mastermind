# app/window.py
"""
Main Window and Title Bar
Enthält die Hauptfenster-Logik und Custom Title Bar
"""
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt
from UI.Views.SettingsView import SettingsView
from UI.Views.GameScreen import GameScreen


class TitleBar(QWidget):
    """Custom title bar with window controls"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setFixedHeight(32)
        self.setStyleSheet("""
            QWidget#TitleBar {
                background: #0f0f14;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 0, 0)
        layout.setSpacing(0)
        
        # Title
        self.title_label = QLabel("SuperHirn - Mastermind")
        self.title_label.setStyleSheet("""
            QLabel {
                color: rgba(245, 245, 255, 0.7);
                font-size: 11px;
                font-weight: 500;
                padding: 0px;
            }
        """)
        layout.addWidget(self.title_label)
        
        layout.addStretch()
        
        # Window controls
        self.minimize_btn = QPushButton("−")
        self.minimize_btn.setObjectName("TitleButton")
        self.minimize_btn.setFixedSize(46, 32)
        self.minimize_btn.setCursor(Qt.PointingHandCursor)
        self.minimize_btn.clicked.connect(self.window().showMinimized)
        layout.addWidget(self.minimize_btn)
        
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setObjectName("TitleButton")
        self.maximize_btn.setFixedSize(46, 32)
        self.maximize_btn.setCursor(Qt.PointingHandCursor)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        layout.addWidget(self.maximize_btn)
        
        self.close_btn = QPushButton("×")
        self.close_btn.setObjectName("TitleButton")
        self.close_btn.setProperty("class", "CloseButton")
        self.close_btn.setFixedSize(46, 32)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.window().close)
        self.close_btn.setStyleSheet("""
            QPushButton#TitleButton {
                background: transparent;
                border: none;
                color: rgba(245, 245, 255, 0.8);
                font-size: 18px;
                font-weight: 300;
            }
            QPushButton#TitleButton:hover {
                background: rgba(220, 50, 50, 0.8);
                color: white;
            }
        """)
        layout.addWidget(self.close_btn)
        
        # Store initial position for dragging
        self._drag_position = None
    
    def toggle_maximize(self):
        if self.window().isMaximized():
            self.window().showNormal()
            self.maximize_btn.setText("□")
        else:
            self.window().showMaximized()
            self.maximize_btn.setText("❐")
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_position is not None:
            self.window().move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_maximize()
            event.accept()


class MainWindow(QMainWindow):
    """
    Main Application Window
    Verwaltet die Views (Settings, Game) und Navigation
    """
    def __init__(self, boundary):
        super().__init__()
        # Remove default title bar
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setWindowTitle("SuperHirn - Mastermind")
        self.resize(1400, 820)

        # Create custom title bar
        self.title_bar = TitleBar(self)
        
        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.title_bar)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # Create views
        self.settings = SettingsView()
        self.settings.set_on_start_callback(self.start_game)

        self.game = GameScreen(boundary)
        self.game.set_on_back_callback(self.back_to_settings)

        # Add views to stack
        self.stack.addWidget(self.settings)
        self.stack.addWidget(self.game)
        self.stack.setCurrentWidget(self.settings)

    def start_game(self):
        """Startet ein neues Spiel mit den Einstellungen aus SettingsView"""
        config = self.settings.get_config()
        success = self.game.initialize_game(config)
        if success:
            self.stack.setCurrentWidget(self.game)

    def back_to_settings(self):
        """Stoppt laufende Spiele und kehrt zur Settings-Ansicht zurück"""
        # Stop any running game threads
        if self.game.game_thread and self.game.game_thread.isRunning():
            self.game.game_thread.terminate()
            self.game.game_thread.wait()

        self.stack.setCurrentWidget(self.settings)
