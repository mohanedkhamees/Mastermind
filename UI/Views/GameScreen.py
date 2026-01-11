# UI/Views/GameScreen.py
from typing import Optional, List, Callable
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox
)
from CoreDomainModel.GameVariant import GameVariant
from CoreDomainModel.Code import Code
from CoreDomainModel.EvaluationResult import EvaluationResult
from CoreDomainModel.GameState import GameState as DomainGameState
from ApplicationControl.GameController import GameController
from ApplicationControl.DelaySynchronizer import DelaySynchronizer
from Implementation.GuessProviders.AIGuessProvider import AIGuessProvider
from Implementation.EvaluationProviders.SystemEvaluationProvider import SystemEvaluationProvider
from Implementation.SecretCodeProviders.SystemSecretCodeProvider import SystemSecretCodeProvider
from Implementation.Algorithms.ConsistencyBasedAlgorithm import ConsistencyBasedAlgorithm
from Implementation.Algorithms.KnuthAlgorithm import KnuthAlgorithm
from UI.Components.BoardWidget import BoardWidget
from UI.Components.InputBar import InputBar
from UI.Components.FeedbackInput import FeedbackInput
from UI.Components.SecretCodeDisplay import SecretCodeDisplay
from UI.Providers.UIGuessProvider import UIGuessProvider
from UI.Providers.UIEvaluationProvider import UIEvaluationProvider
from UI.Providers.UISecretCodeProvider import UISecretCodeProvider
from UI.Listeners.UIGameListener import UIGameListener
from UI.Threads.GameThread import GameThread
from UI.Utils.ColorMapper import (
    PEG_COLOR_MAP, PALETTE_SUPERHIRN, PALETTE_SUPERSUPERHIRN, color_to_peg
)
from UI.Utils.SettingsManager import SettingsManager, GameHistoryEntry
from datetime import datetime


def make_card() -> QFrame:
    f = QFrame()
    f.setObjectName("Card")
    return f


class GameScreen(QWidget):
    """Game screen - implements IGameScreen interface"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.variant: Optional[GameVariant] = None
        self.mode: Optional[str] = None
        self.controller: Optional[GameController] = None
        self.controller1: Optional[GameController] = None
        self.controller2: Optional[GameController] = None
        self.game_thread: Optional[GameThread] = None
        self.game_thread1: Optional[GameThread] = None
        self.game_thread2: Optional[GameThread] = None
        self.ui_guess_provider: Optional[UIGuessProvider] = None
        self.ui_eval_provider: Optional[UIEvaluationProvider] = None
        self.ui_code_provider: Optional[UISecretCodeProvider] = None
        self.listener: Optional[UIGameListener] = None
        self.listener1: Optional[UIGameListener] = None
        self.listener2: Optional[UIGameListener] = None
        self.current_round = 0
        self.current_round1 = 0
        self.current_round2 = 0
        self.last_computer_guess_colors: Optional[List[QColor]] = None
        self.secret_code_colors: Optional[List[QColor]] = None
        self.settings = None
        self.kodierer_mode: Optional[str] = None  # Store kodierer mode

        self._on_back_callback: Optional[Callable] = None

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        # Top bar
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

        root.addLayout(top)

        # Board card
        self.boards_card = make_card()
        root.addWidget(self.boards_card, stretch=1)

        self.boards_layout = QHBoxLayout(self.boards_card)
        self.boards_layout.setContentsMargins(18, 18, 18, 18)
        self.boards_layout.setSpacing(18)

        self.board_widget: Optional[BoardWidget] = None
        self.board_widget1: Optional[BoardWidget] = None
        self.board_widget2: Optional[BoardWidget] = None

        # Input bar (for RATER and KODIERER modes)
        self.input_bar: Optional[InputBar] = None

        # Feedback input (for KODIERER mode)
        self.feedback_input: Optional[FeedbackInput] = None

        # Secret code display (for KODIERER mode)
        self.secret_code_display: Optional[SecretCodeDisplay] = None

        # New game button container (initially hidden)
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

    def get_algorithm(self, variant: GameVariant, algorithm_name: str = "Consistency"):
        """Create algorithm based on name"""
        eval_provider = SystemEvaluationProvider()

        if algorithm_name == "Knuth":
            return KnuthAlgorithm(variant, eval_provider)
        else:
            return ConsistencyBasedAlgorithm(variant, eval_provider)

    def initialize_game(self, variant: GameVariant, mode: str) -> bool:
        """Initialize game based on variant and mode. Returns True if successful, False if connection failed."""
        self.variant = variant
        self.mode = mode
        self.current_round = 0
        self.current_round1 = 0
        self.current_round2 = 0

        # Reset message shown flag
        self._zuschauer_message_shown = False

        # Clear old secret code display
        if self.secret_code_display:
            try:
                self.secret_code_display.setParent(None)
                self.secret_code_display.deleteLater()
            except:
                pass
            self.secret_code_display = None
        self.secret_code_colors = None

        # Clear old input bar
        if self.input_bar:
            try:
                self.input_bar.setParent(None)
                self.input_bar.deleteLater()
            except:
                pass
            self.input_bar = None

        # Clear old feedback input
        if self.feedback_input:
            try:
                self.feedback_input.setParent(None)
                self.feedback_input.deleteLater()
            except:
                pass
            self.feedback_input = None

        # Stop any running threads FIRST
        if self.game_thread:
            try:
                if self.game_thread.isRunning():
                    self.game_thread.terminate()
                    self.game_thread.wait()
            except:
                pass
            self.game_thread = None

        if self.game_thread1:
            try:
                if self.game_thread1.isRunning():
                    self.game_thread1.terminate()
                    self.game_thread1.wait()
            except:
                pass
            self.game_thread1 = None

        if self.game_thread2:
            try:
                if self.game_thread2.isRunning():
                    self.game_thread2.terminate()
                    self.game_thread2.wait()
            except:
                pass
            self.game_thread2 = None

        # Clear boards based on mode
        if mode == "ZUSCHAUER":
            if self.board_widget1:
                try:
                    self.board_widget1.setParent(None)
                    self.board_widget1.deleteLater()
                except:
                    pass
                self.board_widget1 = None

            if self.board_widget2:
                try:
                    self.board_widget2.setParent(None)
                    self.board_widget2.deleteLater()
                except:
                    pass
                self.board_widget2 = None
        else:
            if self.board_widget:
                try:
                    self.board_widget.setParent(None)
                    self.board_widget.deleteLater()
                except:
                    pass
                self.board_widget = None

        # Clear all items from boards_layout
        while self.boards_layout.count():
            item = self.boards_layout.takeAt(0)
            if item and item.widget():
                try:
                    item.widget().deleteLater()
                except:
                    pass

        # Clear controllers and providers
        self.controller = None
        self.controller1 = None
        self.controller2 = None
        self.ui_guess_provider = None
        self.ui_eval_provider = None
        self.ui_code_provider = None

        # Get color palette
        palette = PALETTE_SUPERHIRN if variant == GameVariant.SUPERHIRN else PALETTE_SUPERSUPERHIRN

        # Setup based on mode
        success = False
        if mode == "RATER":
            success = self._setup_rater_mode(palette)
        elif mode == "KODIERER":
            success = self._setup_kodierer_mode(palette)
        elif mode == "ZUSCHAUER":
            success = self._setup_zuschauer_mode(palette)

        if success:
            self.update_status("Bereit zum Starten")
        
        return success

    def _setup_rater_mode(self, palette: List[QColor]) -> bool:
        """Human guesses, computer evaluates. Returns True if successful, False if connection failed."""
        from Implementation.SecretCodeProviders.SystemSecretCodeProvider import SystemSecretCodeProvider
        from Implementation.EvaluationProviders.SystemEvaluationProvider import SystemEvaluationProvider
        from Implementation.EvaluationProviders.RemoteEvaluationProvider import RemoteEvaluationProvider
        from Networking.NetworkService import NetworkService
        from PySide6.QtWidgets import QMessageBox

        rater_mode = self.settings.get_rater_mode() if self.settings else "Local"

        if rater_mode == "Online":
            ip = self.settings.get_server_ip()
            port = self.settings.get_server_port()
            gamer_id = self.settings.get_gamer_id()
            server_url = f"http://{ip}:{port}"

            network_service = NetworkService(server_url, gamer_id=gamer_id)
            eval_provider = RemoteEvaluationProvider(network_service, self.variant)

            if not eval_provider.initialize():
                QMessageBox.warning(self, "Connection Failed", 
                                  f"Cannot connect to server: {server_url}\n"
                                  f"Please check IP and Port.")
                return False

            secret_provider = SystemSecretCodeProvider(self.variant)
            
            guess_provider = UIGuessProvider()
            self.ui_guess_provider = guess_provider

            from CoreDomainModel.Game import Game
            game = Game(self.variant, max_rounds=10)

            self.controller = GameController(
                game=game,
                secret_code_provider=secret_provider,
                guess_provider=guess_provider,
                evaluation_provider=eval_provider
            )

            self.listener = UIGameListener(self)
            self.listener.round_played.connect(self._on_round_played)
            self.listener.game_won.connect(self._on_game_won)
            self.listener.game_lost.connect(self._on_game_lost)
            self.controller.add_listener(self.listener)

            self._create_single_board(palette)
            self._create_input_bar(palette)

            self._start_game_thread()
            return True
        else:
            secret_provider = SystemSecretCodeProvider(self.variant)
            eval_provider = SystemEvaluationProvider()

            guess_provider = UIGuessProvider()
            self.ui_guess_provider = guess_provider

            from CoreDomainModel.Game import Game
            game = Game(self.variant, max_rounds=10)

            self.controller = GameController(
                game=game,
                secret_code_provider=secret_provider,
                guess_provider=guess_provider,
                evaluation_provider=eval_provider
            )

            self.listener = UIGameListener(self)
            self.listener.round_played.connect(self._on_round_played)
            self.listener.game_won.connect(self._on_game_won)
            self.listener.game_lost.connect(self._on_game_lost)
            self.controller.add_listener(self.listener)

            self._create_single_board(palette)
            self._create_input_bar(palette)

            self._start_game_thread()
            return True

    def _setup_kodierer_mode(self, palette: List[QColor]) -> bool:
        """Computer guesses, evaluation depends on Codierer type. Returns True if successful, False if connection failed."""
        from Implementation.GuessProviders.AIGuessProvider import AIGuessProvider
        from Implementation.SecretCodeProviders.SystemSecretCodeProvider import SystemSecretCodeProvider
        from Implementation.EvaluationProviders.SystemEvaluationProvider import SystemEvaluationProvider
        from Implementation.EvaluationProviders.RemoteEvaluationProvider import RemoteEvaluationProvider
        from Networking.NetworkService import NetworkService
        from PySide6.QtWidgets import QMessageBox

        kodierer_mode = self.settings.get_kodierer_mode() if self.settings else "Mensch"
        self.kodierer_mode = kodierer_mode  # Store for later use

        if kodierer_mode == "Mensch":
            # Human creates code, computer guesses, human evaluates
            secret_provider = UISecretCodeProvider()
            self.ui_secret_provider = secret_provider
            self._create_single_board(palette)
            self._create_input_bar(palette)
            return True
        elif kodierer_mode == "lokaler Computer":
            # Computer creates code, computer guesses, computer evaluates
            secret_provider = SystemSecretCodeProvider(self.variant)
            eval_provider = SystemEvaluationProvider()
            
            algorithm_name = self.settings.get_algorithm() if self.settings else "Consistency"
            algorithm = self.get_algorithm(self.variant, algorithm_name)
            algorithm._evaluation_provider = eval_provider
            guess_provider = AIGuessProvider(algorithm)

            from CoreDomainModel.Game import Game
            game = Game(self.variant, max_rounds=10)
            self.controller = GameController(
                game=game,
                secret_code_provider=secret_provider,
                guess_provider=guess_provider,
                evaluation_provider=eval_provider
            )

            self.listener = UIGameListener(self)
            self.listener.round_played.connect(self._on_round_played)
            self.listener.game_won.connect(self._on_game_won)
            self.listener.game_lost.connect(self._on_game_lost)
            self.controller.add_listener(self.listener)

            self.current_round = 0
            self._create_single_board(palette)
            self._start_game_thread()
            return True
        elif kodierer_mode == "Codierer im Netz":
            # Server creates code, computer guesses, server evaluates
            ip = self.settings.get_kodierer_server_ip()
            port = self.settings.get_kodierer_server_port()
            gamer_id = self.settings.get_kodierer_gamer_id()
            server_url = f"http://{ip}:{port}"

            network_service = NetworkService(server_url, gamer_id=gamer_id)
            eval_provider = RemoteEvaluationProvider(network_service, self.variant)

            if not eval_provider.initialize():
                QMessageBox.warning(self, "Connection Failed", 
                                  f"Cannot connect to Codierer server: {server_url}\n"
                                  f"Please check IP and Port.")
                return False

            secret_provider = SystemSecretCodeProvider(self.variant)
            
            # For consistency checking, use local SystemEvaluationProvider
            # RemoteEvaluationProvider is only for actual game evaluation
            # get_algorithm() already creates SystemEvaluationProvider internally
            algorithm_name = self.settings.get_algorithm() if self.settings else "Consistency"
            algorithm = self.get_algorithm(self.variant, algorithm_name)
            # Don't set algorithm._evaluation_provider = eval_provider
            # The algorithm uses SystemEvaluationProvider for consistency checking
            guess_provider = AIGuessProvider(algorithm)

            from CoreDomainModel.Game import Game
            game = Game(self.variant, max_rounds=10)
            self.controller = GameController(
                game=game,
                secret_code_provider=secret_provider,
                guess_provider=guess_provider,
                evaluation_provider=eval_provider
            )

            self.listener = UIGameListener(self)
            self.listener.round_played.connect(self._on_round_played)
            self.listener.game_won.connect(self._on_game_won)
            self.listener.game_lost.connect(self._on_game_lost)
            self.controller.add_listener(self.listener)

            self.current_round = 0
            self._create_single_board(palette)
            self._start_game_thread()
            return True

    def _on_secret_code_submitted(self, colors: List[QColor]):
        """User submitted secret code (Kodierer mode)"""
        # Convert colors to PegColors
        pegs = [color_to_peg(c) for c in colors]

        # Validate that we have the correct number of pegs
        if len(pegs) != self.variant.code_length:
            QMessageBox.warning(self, "Ungültiger Code", 
                              f"Der Code muss {self.variant.code_length} Farben haben!")
            return

        # Store secret code for display
        self.secret_code_colors = colors

        # Setup providers FIRST
        self.ui_code_provider = UISecretCodeProvider()
        
        # Show secret code display IMMEDIATELY (so user can see it)
        self._show_secret_code_display(colors)

        # Computer will guess, but HUMAN will evaluate
        # NOTE: Server is NOT used in Kodierer mode because HUMAN evaluates
        algorithm_name = self.settings.get_algorithm() if self.settings else "Consistency"
        algorithm = self.get_algorithm(self.variant, algorithm_name)
        guess_provider = AIGuessProvider(algorithm)
        self.ui_eval_provider = UIEvaluationProvider()

        # Create game with max_rounds=10
        from CoreDomainModel.Game import Game
        game = Game(self.variant, max_rounds=10)
        self.controller = GameController(
            game=game,
            guess_provider=guess_provider,
            evaluation_provider=self.ui_eval_provider,
            secret_code_provider=self.ui_code_provider
        )

        # Setup listener
        self.listener = UIGameListener(self)
        self.listener.round_played.connect(self._on_round_played)
        self.listener.game_won.connect(self._on_game_won)
        self.listener.game_lost.connect(self._on_game_lost)
        self.controller.add_listener(self.listener)

        # Hide input bar
        self.input_bar.hide()

        # Create feedback input UI
        self._create_feedback_input()

        # NOW set the code (after controller is created and ready)
        # This must be done BEFORE starting the thread, so the code is available when create_secret_code is called
        self.ui_code_provider.set_code(pegs)

        # Start game in thread (code is already set, so create_secret_code will return it immediately)
        self._start_game_thread()

    def _show_secret_code_display(self, colors: List[QColor]):
        """Display the secret code so user can give correct feedback"""
        if self.secret_code_display:
            try:
                self.secret_code_display.setParent(None)
                self.secret_code_display.deleteLater()
            except:
                pass
            self.secret_code_display = None

        self.secret_code_display = SecretCodeDisplay()
        self.secret_code_display.display_code(colors)
        self.layout().insertWidget(2, self.secret_code_display)

    def _create_input_bar(self, palette: List[QColor]):
        """Create input bar for guesses or secret code entry"""
        if self.input_bar:
            try:
                self.input_bar.setParent(None)
                self.input_bar.deleteLater()
            except:
                pass

        self.input_bar = InputBar(self.variant.code_length, palette)
        # Connect to a handler that routes based on mode
        self.input_bar.submitted.connect(self._on_input_submitted)
        self.layout().insertWidget(1, self.input_bar)

    def _on_input_submitted(self, colors: List[QColor]):
        """Route input submission based on current mode"""
        if self.mode == "KODIERER":
            # Check if controller exists - if not, it's secret code submission
            if not hasattr(self, 'controller') or self.controller is None:
                # Secret code submission (before game starts)
                self._on_secret_code_submitted(colors)
            # If controller exists, ignore (game already started)
        elif self.mode == "RATER":
            # Guess submission
            self._on_guess_submitted(colors)

    def _create_single_board(self, palette: List[QColor]):
        """Create a single board widget for Rater/Kodierer modes"""
        if self.board_widget:
            try:
                self.board_widget.setParent(None)
                self.board_widget.deleteLater()
            except:
                pass
        self.board_widget = None

        # Clear all items from boards_layout to ensure no old boards remain
        while self.boards_layout.count():
            item = self.boards_layout.takeAt(0)
            if item and item.widget():
                try:
                    item.widget().setParent(None)
                    item.widget().deleteLater()
                except:
                    pass

        self.board_widget = BoardWidget(self.variant, "")
        self.boards_layout.addWidget(self.board_widget)

    def _create_dual_boards(self, palette: List[QColor], algorithm1_name: str, algorithm2_name: str):
        """Create two board widgets for Zuschauer mode"""
        # Clear existing boards
        if self.board_widget1:
            try:
                self.board_widget1.setParent(None)
                self.board_widget1.deleteLater()
            except:
                pass
        if self.board_widget2:
            try:
                self.board_widget2.setParent(None)
                self.board_widget2.deleteLater()
            except:
                pass

        # Create two boards with algorithm names
        self.board_widget1 = BoardWidget(self.variant, f"Board 1: {algorithm1_name}")
        self.board_widget2 = BoardWidget(self.variant, f"Board 2: {algorithm2_name}")
        
        self.boards_layout.addWidget(self.board_widget1)
        self.boards_layout.addWidget(self.board_widget2)

    def _create_feedback_input(self):
        """Create UI1 for human to give feedback"""
        if self.feedback_input:
            try:
                self.feedback_input.setParent(None)
                self.feedback_input.deleteLater()
            except:
                pass

        self.feedback_input = FeedbackInput(self.variant.code_length)
        self.feedback_input.submitted.connect(self._on_feedback_submitted)
        self.feedback_input.hide()
        self.layout().insertWidget(1, self.feedback_input)

    def _on_feedback_submitted(self, black: int, white: int):
        """User submitted feedback for computer's guess"""
        if self.ui_eval_provider is None:
            return

        # Validate feedback
        max_pegs = self.variant.code_length
        if black + white > max_pegs:
            QMessageBox.warning(self, "Ungültiges Feedback",
                                f"Schwarz + Weiß darf nicht größer als {max_pegs} sein!")
            return

        # Get the current guess from stored colors
        if not self.last_computer_guess_colors:
            return

        guess_colors = self.last_computer_guess_colors

        # Update the current row with feedback
        if self.board_widget and self.current_round < len(self.board_widget.rows):
            row = self.board_widget.rows[self.current_round]
            row.set_feedback(black, white)
            self.board_widget.update()
            self.current_round += 1

        # Give feedback to computer
        self.ui_eval_provider.set_feedback(black, white)

        # Reset feedback input
        self.feedback_input.reset()
        self.feedback_input.hide()
        self.update_status("Warte auf nächsten Zug des Computers...")

        # Clear stored guess
        self.last_computer_guess_colors = None

    def _setup_zuschauer_mode(self, palette: List[QColor]) -> bool:
        """Computer vs Computer (both can optionally use server)"""
        from Implementation.SecretCodeProviders.SystemSecretCodeProvider import SystemSecretCodeProvider
        from Implementation.EvaluationProviders.SystemEvaluationProvider import SystemEvaluationProvider
        from Implementation.GuessProviders.AIGuessProvider import AIGuessProvider
        from Implementation.Algorithms.ConsistencyBasedAlgorithm import ConsistencyBasedAlgorithm
        from Implementation.Algorithms.KnuthAlgorithm import KnuthAlgorithm
        from ApplicationControl.DelaySynchronizer import DelaySynchronizer

        # Get settings
        algorithm1_name = self.settings.get_algorithm1() if self.settings else "Consistency"
        algorithm2_name = self.settings.get_algorithm2() if self.settings else "Consistency"
        delay = self.settings.get_delay() if self.settings else 1

        # Create two games
        from CoreDomainModel.Game import Game
        game1 = Game(self.variant, max_rounds=10)
        game2 = Game(self.variant, max_rounds=10)

        # Create secret code (same for both boards for fair comparison)
        secret_provider_base = SystemSecretCodeProvider(self.variant)
        secret_code = secret_provider_base.create_secret_code()
        
        # Create providers that return the same code
        class SameCodeProvider(SystemSecretCodeProvider):
            def __init__(self, variant, code):
                super().__init__(variant)
                self._fixed_code = code
            
            def create_secret_code(self) -> Code:
                return self._fixed_code
        
        secret_provider1 = SameCodeProvider(self.variant, secret_code)
        secret_provider2 = SameCodeProvider(self.variant, secret_code)

        # Use local evaluation providers
        eval_provider1 = SystemEvaluationProvider()
        eval_provider2 = SystemEvaluationProvider()

        # Create algorithms and guess providers
        algorithm1 = self.get_algorithm(self.variant, algorithm1_name)
        algorithm1._evaluation_provider = eval_provider1
        guess_provider1 = AIGuessProvider(algorithm1)

        algorithm2 = self.get_algorithm(self.variant, algorithm2_name)
        algorithm2._evaluation_provider = eval_provider2
        guess_provider2 = AIGuessProvider(algorithm2)

        # Create controllers
        self.controller1 = GameController(
            game=game1,
            secret_code_provider=secret_provider1,
            guess_provider=guess_provider1,
            evaluation_provider=eval_provider1
        )

        self.controller2 = GameController(
            game=game2,
            secret_code_provider=secret_provider2,
            guess_provider=guess_provider2,
            evaluation_provider=eval_provider2
        )

        # Setup delay synchronizer
        delay_sync = DelaySynchronizer(delay)

        # Setup listeners
        self.listener1 = UIGameListener(self)
        self.listener1.round_played.connect(lambda g, r: self._on_round_played(g, r, 1))
        self.listener1.game_won.connect(lambda: self._on_game_won(1))
        self.listener1.game_lost.connect(lambda: self._on_game_lost(1))
        self.controller1.add_listener(self.listener1)

        self.listener2 = UIGameListener(self)
        self.listener2.round_played.connect(lambda g, r: self._on_round_played(g, r, 2))
        self.listener2.game_won.connect(lambda: self._on_game_won(2))
        self.listener2.game_lost.connect(lambda: self._on_game_lost(2))
        self.controller2.add_listener(self.listener2)

        # Create two boards
        self._create_dual_boards(palette, algorithm1_name, algorithm2_name)

        # Start both games in threads
        self._start_parallel_game_threads(delay)
        return True

    def _start_game_thread(self):
        """Start game in background thread"""
        if self.controller is None:
            return

        # Check if human evaluates (only in KODIERER mode with Mensch as Codierer)
        is_human_evaluator = False
        if self.mode == "KODIERER":
            # Use stored kodierer_mode instead of reading from settings
            kodierer_mode = self.kodierer_mode if self.kodierer_mode else "Mensch"
            is_human_evaluator = (kodierer_mode == "Mensch")

        self.game_thread = GameThread(self.controller, self, is_human_evaluator=is_human_evaluator)
        self.game_thread.finished.connect(lambda: self._on_game_finished())
        self.game_thread.error.connect(self._on_game_error)

        if is_human_evaluator:
            self.game_thread.computer_guessed.connect(self.show_computer_guess)
            self.game_thread.waiting_for_feedback.connect(self._on_waiting_for_feedback)

        self.game_thread.start()
        self.update_status("Spiel läuft...")

    def _start_parallel_game_threads(self, delay_seconds: int):
        """Start both games in parallel threads"""
        delay = DelaySynchronizer(delay_seconds) if delay_seconds > 0 else None

        self.game_thread1 = GameThread(self.controller1, self, is_human_evaluator=False, delay=delay)
        self.game_thread1.finished.connect(lambda: self._on_game_finished(1))
        self.game_thread1.error.connect(lambda msg: self._on_game_error(msg, 1))

        self.game_thread2 = GameThread(self.controller2, self, is_human_evaluator=False, delay=delay)
        self.game_thread2.finished.connect(lambda: self._on_game_finished(2))
        self.game_thread2.error.connect(lambda msg: self._on_game_error(msg, 2))

        self.game_thread1.start()
        self.game_thread2.start()

        self.update_status(f"Beide Spiele laufen parallel (Delay: {delay_seconds}s)...")

    def _on_guess_submitted(self, colors: List[QColor]):
        """User submitted a guess (RATER mode)"""
        if self.ui_guess_provider is None:
            return

        pegs = [color_to_peg(c) for c in colors]
        self.ui_guess_provider.set_guess(pegs)
        self.input_bar.set_enabled(False)
        self.update_status("Warte auf Feedback...")

    def display_round(self, guess: Code, result: EvaluationResult, board: int = 0):
        """Display a completed round"""
        # For KODIERER mode with Mensch, skip - handled by on_feedback_submitted
        if self.mode == "KODIERER":
            kodierer_mode = self.settings.get_kodierer_mode() if self.settings else "Mensch"
            if kodierer_mode == "Mensch":
                return

        # Convert guess to QColors
        guess_colors = []
        for peg in guess.get_pegs():
            color = PEG_COLOR_MAP.get(peg, QColor("#ffffff"))
            guess_colors.append(color)

        black = result.correct_position
        white = result.correct_color

        # Update UI1 on main thread
        if self.mode == "ZUSCHAUER":
            QTimer.singleShot(0, lambda gc=guess_colors, b=black, w=white, brd=board:
            self._update_round_ui(gc, b, w, brd))
        else:
            QTimer.singleShot(0, lambda gc=guess_colors, b=black, w=white:
            self._update_round_ui(gc, b, w))

    def _update_round_ui(self, guess_colors: List[QColor], black: int, white: int, board: int = 0):
        """Update UI1 with new round"""
        if self.mode == "ZUSCHAUER":
            if board == 1:
                if self.board_widget1:
                    self.board_widget1.add_round(guess_colors, black, white)
                    self.current_round1 += 1
            elif board == 2:
                if self.board_widget2:
                    self.board_widget2.add_round(guess_colors, black, white)
                    self.current_round2 += 1
            self.update_status(f"Board 1: {self.current_round1} Runden | Board 2: {self.current_round2} Runden")
        else:
            if not self.board_widget:
                print(f"[ERROR] board_widget is None in mode {self.mode}")
                return
            
            self.board_widget.add_round(guess_colors, black, white)
            self.current_round += 1
            # Force repaint
            self.board_widget.update()
            self.update()

            if self.mode == "RATER" and self.input_bar:
                self.input_bar.set_enabled(True)
                self.update_status("Dein Zug...")
            elif self.mode == "KODIERER":
                self.update_status(f"Runde {self.current_round}: Computer rät weiter...")

    def show_computer_guess(self, guess: Code):
        """Show computer's guess (Kodierer mode)"""
        guess_colors = []
        for peg in guess.get_pegs():
            color = PEG_COLOR_MAP.get(peg, QColor("#ffffff"))
            guess_colors.append(color)

        self.last_computer_guess_colors = guess_colors

        if self.board_widget and self.current_round < len(self.board_widget.rows):
            row = self.board_widget.rows[self.current_round]
            row.set_guess(guess_colors)
            self.board_widget.update()

    def _on_waiting_for_feedback(self):
        """Called when computer is waiting for feedback"""
        if self.feedback_input:
            self.feedback_input.show()
            self.update_status("Computer hat geraten. Gib Feedback...")

    def _on_round_played(self, guess: Code, result: EvaluationResult, board: int = 0):
        """Called when a round is completed"""
        # Skip for Kodierer mode with Mensch (handled by _on_feedback_submitted)
        if self.mode == "KODIERER":
            # Use stored kodierer_mode instead of reading from settings
            kodierer_mode = self.kodierer_mode if self.kodierer_mode else "Mensch"
            
            if kodierer_mode == "Mensch":
                return
        
        # Convert guess to colors
        guess_colors = []
        for peg in guess.get_pegs():
            color = PEG_COLOR_MAP.get(peg, QColor("#ffffff"))
            guess_colors.append(color)
        
        black = result.correct_position
        white = result.correct_color
        
        # Update UI directly (QTimer might not work in background thread)
        if self.mode == "ZUSCHAUER":
            QTimer.singleShot(0, lambda gc=guess_colors, b=black, w=white, brd=board:
            self._update_round_ui(gc, b, w, brd))
        else:
            # For KODIERER with lokaler Computer or Codierer im Netz, update directly
            self._update_round_ui(guess_colors, black, white)

    def show_game_won(self, rounds: int, board: int = 0):
        """Show game won message"""
        QTimer.singleShot(0, lambda r=rounds, b=board: self._show_win(r, b))

    def _show_win(self, rounds: int, board: int = 0):
        if self.mode == "ZUSCHAUER":
            if self.game_thread1 and self.game_thread2:
                if (not self.game_thread1.isRunning() and not self.game_thread2.isRunning()):
                    # Only show message once (use a flag to prevent duplicate)
                    if not hasattr(self, '_zuschauer_message_shown') or not self._zuschauer_message_shown:
                        self._zuschauer_message_shown = True
                        
                        # Get accurate round counts and states from game objects
                        rounds1 = len(self.controller1._game.get_rounds()) if self.controller1 else self.current_round1
                        rounds2 = len(self.controller2._game.get_rounds()) if self.controller2 else self.current_round2
                        state1 = self.controller1._game.get_state() if self.controller1 else None
                        state2 = self.controller2._game.get_state() if self.controller2 else None
                        
                        # Determine results for each board
                        board1_result = "gewonnen" if (state1 and state1.value == "WON") else "verloren"
                        board2_result = "gewonnen" if (state2 and state2.value == "WON") else "verloren"
                        
                        # Determine who was faster (less rounds = faster)
                        if rounds1 < rounds2:
                            faster_text = "Board 1 war schneller"
                        elif rounds2 < rounds1:
                            faster_text = "Board 2 war schneller"
                        else:
                            faster_text = "Beide Boards gleich schnell"
                        
                        # Build status text
                        result_text = f"Board 1 hat mit {rounds1} Runden {board1_result} || Board 2 hat mit {rounds2} Runden {board2_result}"
                        
                        # Update status at the top (without emoji and !)
                        self.update_status(result_text)
                        
                        # Show modern alert message with three rows
                        msg = QMessageBox(self)
                        msg.setWindowTitle("Spiele beendet")
                        msg.setText(f"<div style='font-size: 16px; padding: 15px; line-height: 1.8;'>"
                                   f"<p style='margin: 8px 0; color: #a080ff; font-weight: bold;'>Board 1: {rounds1} Runden - {board1_result.capitalize()}</p>"
                                   f"<p style='margin: 8px 0; color: #a080ff; font-weight: bold;'>Board 2: {rounds2} Runden - {board2_result.capitalize()}</p>"
                                   f"<p style='margin: 8px 0; color: #fdd835; font-weight: bold; font-size: 18px;'>{faster_text}</p>"
                                   f"</div>")
                        msg.setIcon(QMessageBox.NoIcon)  # Remove icon
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
                        
                        # Show "Neues Spiel" button only when both games are finished
                        self._show_new_game_button()
                else:
                    # One board won, but other still running - don't show button yet
                    self.update_status(f"Board {board} gewonnen in {rounds} Runden")
            else:
                self.update_status(f"Board {board} gewonnen in {rounds} Runden")
        else:
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
                variant=self.variant.name,
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
        # Show "Neues Spiel" button
        self._show_new_game_button()

    def show_game_lost(self, rounds: int, board: int = 0):
        """Show game lost message"""
        QTimer.singleShot(0, lambda r=rounds, b=board: self._show_loss(r, b))

    def _show_loss(self, rounds: int, board: int = 0):
        if self.mode == "ZUSCHAUER":
            # Check if both games are finished
            if self.game_thread1 and self.game_thread2:
                if (not self.game_thread1.isRunning() and not self.game_thread2.isRunning()):
                    # Only show message once (use a flag to prevent duplicate)
                    if not hasattr(self, '_zuschauer_message_shown') or not self._zuschauer_message_shown:
                        self._zuschauer_message_shown = True
                        
                        # Get accurate round counts and states from game objects
                        rounds1 = len(self.controller1._game.get_rounds()) if self.controller1 else self.current_round1
                        rounds2 = len(self.controller2._game.get_rounds()) if self.controller2 else self.current_round2
                        state1 = self.controller1._game.get_state() if self.controller1 else None
                        state2 = self.controller2._game.get_state() if self.controller2 else None
                        
                        # Determine results for each board
                        board1_result = "gewonnen" if (state1 and state1.value == "WON") else "verloren"
                        board2_result = "gewonnen" if (state2 and state2.value == "WON") else "verloren"
                        
                        # Determine who was faster (less rounds = faster)
                        if rounds1 < rounds2:
                            faster_text = "Board 1 war schneller"
                        elif rounds2 < rounds1:
                            faster_text = "Board 2 war schneller"
                        else:
                            faster_text = "Beide Boards gleich schnell"
                        
                        # Build status text
                        result_text = f"Board 1 hat mit {rounds1} Runden {board1_result} || Board 2 hat mit {rounds2} Runden {board2_result}"
                        
                        # Update status at the top (without emoji and !)
                        self.update_status(result_text)
                        
                        # Show secret code if both games lost
                        if board1_result == "verloren" and board2_result == "verloren":
                            # Get secret code from controller1 (both use same code)
                            if self.controller1 and self.controller1._secret_code:
                                secret_code_colors = []
                                for peg in self.controller1._secret_code.get_pegs():
                                    color = PEG_COLOR_MAP.get(peg, QColor("#ffffff"))
                                    secret_code_colors.append(color)
                                if secret_code_colors:
                                    self._show_secret_code_display(secret_code_colors)
                        
                        # Show modern alert message with three rows
                        msg = QMessageBox(self)
                        msg.setWindowTitle("Spiele beendet")
                        msg.setText(f"<div style='font-size: 16px; padding: 15px; line-height: 1.8;'>"
                                   f"<p style='margin: 8px 0; color: #a080ff; font-weight: bold;'>Board 1: {rounds1} Runden - {board1_result.capitalize()}</p>"
                                   f"<p style='margin: 8px 0; color: #a080ff; font-weight: bold;'>Board 2: {rounds2} Runden - {board2_result.capitalize()}</p>"
                                   f"<p style='margin: 8px 0; color: #fdd835; font-weight: bold; font-size: 18px;'>{faster_text}</p>"
                                   f"</div>")
                        msg.setIcon(QMessageBox.NoIcon)  # Remove icon
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
                        
                        # Show "Neues Spiel" button only when both games are finished
                        self._show_new_game_button()
                else:
                    # One board lost, but other still running - don't show button yet
                    self.update_status(f"Board {board} verloren nach {rounds} Runden")
            else:
                self.update_status(f"Board {board} verloren nach {rounds} Runden")
        else:
            self.update_status("Verloren")
            stats = SettingsManager.load_stats()
            stats.games_played += 1
            stats.total_rounds += rounds
            SettingsManager.save_stats(stats)

            SettingsManager.add_history_entry(GameHistoryEntry(
                mode=self.mode,
                variant=self.variant.name,
                won=False,
                rounds=rounds,
                timestamp=datetime.now().isoformat()
            ))

            # Get secret code and convert to colors
            # Only show secret code if it's available locally (not on remote server)
            secret_code_colors = []
            if self.controller and self.controller._secret_code:
                # Check if evaluation provider is remote (code is on server, not available locally)
                from Implementation.EvaluationProviders.RemoteEvaluationProvider import RemoteEvaluationProvider
                is_remote = isinstance(self.controller._evaluation_provider, RemoteEvaluationProvider)
                
                # Only show code if it's not on remote server
                if not is_remote:
                    for peg in self.controller._secret_code.get_pegs():
                        color = PEG_COLOR_MAP.get(peg, QColor("#ffffff"))
                        secret_code_colors.append(color)
            
            # Show secret code display if we have the code
            if secret_code_colors:
                self._show_secret_code_display(secret_code_colors)

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

    def _show_new_game_button(self):
        """Show the new game button after game ends"""
        if self.new_game_container:
            self.new_game_container.show()

    def _on_game_end_message_closed(self, button):
        """Called when game end message (OK button) is clicked"""
        # Show "Neues Spiel" button after OK is clicked
        self._show_new_game_button()

    def _on_new_game_clicked(self):
        """Handle new game button click - go back to settings"""
        # Hide new game button
        if self.new_game_container:
            self.new_game_container.hide()
        
        # Go back to settings screen
        if self._on_back_callback:
            self._on_back_callback()

    def _on_game_won(self, board: int = 0):
        """Game won signal handler"""
        if self.mode == "ZUSCHAUER":
            # Get rounds from game object (more accurate)
            if board == 1 and self.controller1:
                rounds = len(self.controller1._game.get_rounds())
            elif board == 2 and self.controller2:
                rounds = len(self.controller2._game.get_rounds())
            else:
                rounds = self.current_round1 if board == 1 else self.current_round2
            self.show_game_won(rounds, board)
        else:
            # Get rounds from game object (more accurate)
            if self.controller:
                rounds = len(self.controller._game.get_rounds())
            else:
                rounds = self.current_round
            self.show_game_won(rounds)

    def _on_game_lost(self, board: int = 0):
        """Game lost signal handler"""
        if self.mode == "ZUSCHAUER":
            # Get rounds from game object (more accurate)
            if board == 1 and self.controller1:
                rounds = len(self.controller1._game.get_rounds())
            elif board == 2 and self.controller2:
                rounds = len(self.controller2._game.get_rounds())
            else:
                rounds = self.current_round1 if board == 1 else self.current_round2
            self.show_game_lost(rounds, board)
        else:
            # Get rounds from game object (more accurate)
            if self.controller:
                rounds = len(self.controller._game.get_rounds())
            else:
                rounds = self.current_round
            self.show_game_lost(rounds)

    def _on_game_finished(self, board: int = 0):
        """Game thread finished"""
        if self.mode == "ZUSCHAUER":
            self.update_status(f"Board {board} beendet")
        else:
            self.update_status("Spiel beendet")

    def _on_game_error(self, error_msg: str, board: int = 0):
        """Game thread error"""
        if self.mode == "ZUSCHAUER":
            QMessageBox.critical(self, f"Fehler Board {board}", f"Spiel-Fehler: {error_msg}")
            self.update_status(f"Fehler aufgetreten (Board {board})")
        else:
            QMessageBox.critical(self, "Fehler", f"Spiel-Fehler: {error_msg}")
            self.update_status("Fehler aufgetreten")

    def update_status(self, message: str):
        self.status_label.setText(message)

    # Add these methods to SettingsView class:

    def get_use_remote_server(self) -> bool:
        """Get whether remote server is enabled"""
        return self.use_remote_server.isChecked()

    def get_server_url(self) -> str:
        """Get server URL"""
        return self.server_url_input.text() if self.use_remote_server.isChecked() else None