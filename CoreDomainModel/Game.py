from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import time
from CoreDomainModel.AlgorithmType import AlgorithmType
from CoreDomainModel.Code import Code
from CoreDomainModel.GameConfig import GameConfig
from CoreDomainModel.GameMode import GameMode
from CoreDomainModel.GameState import GameState
from CoreDomainModel.GameVariant import GameVariant
from CoreDomainModel.IGame import IGame
from CoreDomainModel.IEvaluationProvider import IEvaluationProvider
from CoreDomainModel.IGuessProvider import IGuessProvider
from CoreDomainModel.ISecretCodeProvider import ISecretCodeProvider
from CoreDomainModel.ProviderFactory import IProviderFactory
from CoreDomainModel.Round import Round


@dataclass
class _GameSession:
    secret_code_provider: ISecretCodeProvider
    guess_provider: IGuessProvider
    evaluation_provider: IEvaluationProvider
    rounds: List[Round]
    state: GameState
    secret_code: Optional[Code]
    is_human_evaluator: bool = False
    pending_guess: Optional[Code] = None


class _FixedSecretCodeProvider(ISecretCodeProvider):
    def __init__(self, code: Code):
        self._code = code

    def create_secret_code(self) -> Code:
        return self._code


class Game(IGame):
    def __init__(self, provider_factory: IProviderFactory, max_rounds: int = 10):
        self._provider_factory = provider_factory
        self._max_rounds = max_rounds
        self._event_sink = None
        self._config: Optional[GameConfig] = None
        self._sessions: List[_GameSession] = []
        self._view: Dict[str, Any] = {}
        self._phase: str = "AUTO_RUNNING"
        self._current_guess: Optional[str] = None

    def start(self, config: Dict[str, Any]) -> bool:
        try:
            self._config = self._parse_config(config)
            self._sessions = []
            self._current_guess = None
            self._setup_sessions()
            self._initialize_phase()
            self._build_view()
            return True
        except Exception as exc:
            self._view = {"error": str(exc)}
            return False

    def play(self) -> None:
        if not self._sessions or not self._config:
            raise RuntimeError("Game not initialized")
        if self._config.mode == GameMode.ZUSCHAUER:
            self._play_parallel()
        elif self._config.mode == GameMode.KODIERER and self._config.kodierer_mode == "Mensch":
            return
        elif self._config.mode == GameMode.RATER:
            return
        else:
            self._play_single(self._sessions[0], board=0)

    def submit_guess(self, colors: List[str]) -> None:
        if not self._sessions or not self._config:
            return
        if self._config.mode != GameMode.RATER:
            return
        session = self._sessions[0]
        if session.state == GameState.NOT_STARTED:
            session.state = GameState.RUNNING
        if session.secret_code is None:
            session.secret_code = session.secret_code_provider.create_secret_code()
        guess = Code.from_color_names(colors)
        result = session.evaluation_provider.evaluate(session.secret_code, guess)
        self._process_round(session, guess, result, board=0)
        self._phase = "WAITING_FOR_GUESS" if self._session_is_running(session) else "AUTO_RUNNING"
        self._build_view()

    def submit_feedback(self, black: int, white: int) -> None:
        if not self._sessions or not self._config:
            return
        session = self._sessions[0]
        if not session.pending_guess:
            return
        session.evaluation_provider.set_feedback(black, white)
        result = session.evaluation_provider.evaluate(session.secret_code, session.pending_guess)
        guess = session.pending_guess
        session.pending_guess = None
        self._current_guess = None
        self._process_round(session, guess, result, board=0)
        if self._session_is_running(session):
            self._produce_computer_guess(session, board=0)
        self._build_view()

    def submit_secret_code(self, colors: List[str]) -> None:
        if self._sessions:
            session = self._sessions[0]
            session.secret_code_provider.set_code(colors)
            session.secret_code = session.secret_code_provider.create_secret_code()
            if session.state == GameState.NOT_STARTED:
                session.state = GameState.RUNNING
            if self._config and self._config.mode == GameMode.KODIERER and session.is_human_evaluator:
                self._produce_computer_guess(session, board=0)
            self._build_view()

    def step(self) -> None:
        if not self._sessions or not self._config:
            return
        if self._config.mode == GameMode.ZUSCHAUER:
            self._step_spectator()
        elif self._config.mode == GameMode.KODIERER and not self._sessions[0].is_human_evaluator:
            if self._session_is_running(self._sessions[0]):
                self._run_single_round(self._sessions[0], board=0)
        self._build_view()

    def get_view(self) -> Dict[str, Any]:
        return self._view

    def set_event_sink(self, sink: Any) -> None:
        self._event_sink = sink

    def _parse_config(self, config: Dict[str, Any]) -> GameConfig:
        variant_name = config.get("variant", "SUPERHIRN")
        try:
            variant = GameVariant[variant_name]
        except KeyError:
            variant = GameVariant.SUPERHIRN

        mode_name = config.get("mode", "RATER")
        try:
            mode = GameMode[mode_name]
        except KeyError:
            mode = GameMode.RATER

        algorithm = self._parse_algorithm(config.get("algorithm", "Consistency"))
        algorithm1 = self._parse_algorithm(config.get("algorithm1", "Consistency"))
        algorithm2 = self._parse_algorithm(config.get("algorithm2", "Consistency"))
        delay_seconds = int(config.get("delay", 1) or 0)
        rater_mode = config.get("rater_mode", "Local")
        kodierer_mode = config.get("kodierer_mode", "Mensch")

        return GameConfig(
            raw=config,
            variant=variant,
            mode=mode,
            algorithm=algorithm,
            algorithm1=algorithm1,
            algorithm2=algorithm2,
            delay_seconds=delay_seconds,
            rater_mode=rater_mode,
            kodierer_mode=kodierer_mode
        )

    def _parse_algorithm(self, value: str) -> AlgorithmType:
        for alg in AlgorithmType:
            if value == alg.value or value.upper() == alg.name:
                return alg
        return AlgorithmType.CONSISTENCY

    def _setup_sessions(self) -> None:
        if not self._config:
            raise RuntimeError("Missing configuration")

        if self._config.mode == GameMode.ZUSCHAUER:
            self._setup_zuschauer_sessions()
        else:
            self._setup_single_session()

    def _initialize_phase(self) -> None:
        if not self._config or not self._sessions:
            return
        session = self._sessions[0]
        if self._config.mode == GameMode.RATER:
            session.secret_code = session.secret_code_provider.create_secret_code()
            session.state = GameState.RUNNING
            self._phase = "WAITING_FOR_GUESS"
        elif self._config.mode == GameMode.KODIERER:
            if session.is_human_evaluator:
                self._phase = "WAITING_FOR_GUESS"
            else:
                session.secret_code = session.secret_code_provider.create_secret_code()
                session.state = GameState.RUNNING
                self._phase = "AUTO_RUNNING"
        else:
            for spectator_session in self._sessions:
                spectator_session.state = GameState.RUNNING
            self._phase = "AUTO_RUNNING"

    def _setup_single_session(self) -> None:
        variant = self._config.variant
        eval_provider = self._provider_factory.create_evaluation_provider(variant, self._config)
        guess_provider = self._provider_factory.create_guess_provider(
            variant,
            self._config,
            eval_provider,
            algorithm=self._config.algorithm
        )
        secret_provider = self._provider_factory.create_secret_code_provider(variant, self._config)
        session = _GameSession(
            secret_code_provider=secret_provider,
            guess_provider=guess_provider,
            evaluation_provider=eval_provider,
            rounds=[],
            state=GameState.NOT_STARTED,
            secret_code=None,
            is_human_evaluator=(self._config.mode == GameMode.KODIERER and self._config.kodierer_mode == "Mensch")
        )
        self._sessions.append(session)

    def _setup_zuschauer_sessions(self) -> None:
        variant = self._config.variant
        base_secret_provider = self._provider_factory.create_secret_code_provider(variant, self._config)
        secret_code = base_secret_provider.create_secret_code()

        eval_provider1 = self._provider_factory.create_evaluation_provider(variant, self._config)
        eval_provider2 = self._provider_factory.create_evaluation_provider(variant, self._config)

        guess_provider1 = self._provider_factory.create_guess_provider(
            variant,
            self._config,
            eval_provider1,
            algorithm=self._config.algorithm1
        )
        guess_provider2 = self._provider_factory.create_guess_provider(
            variant,
            self._config,
            eval_provider2,
            algorithm=self._config.algorithm2
        )

        self._sessions.append(_GameSession(
            secret_code_provider=_FixedSecretCodeProvider(secret_code),
            guess_provider=guess_provider1,
            evaluation_provider=eval_provider1,
            rounds=[],
            state=GameState.NOT_STARTED,
            secret_code=secret_code
        ))
        self._sessions.append(_GameSession(
            secret_code_provider=_FixedSecretCodeProvider(secret_code),
            guess_provider=guess_provider2,
            evaluation_provider=eval_provider2,
            rounds=[],
            state=GameState.NOT_STARTED,
            secret_code=secret_code
        ))

    def _produce_computer_guess(self, session: _GameSession, board: int) -> None:
        if session.secret_code is None:
            session.secret_code = session.secret_code_provider.create_secret_code()
        if session.state == GameState.NOT_STARTED:
            session.state = GameState.RUNNING
        guess = session.guess_provider.next_guess()
        session.pending_guess = guess
        self._current_guess = " ".join(guess.to_color_names())
        self._phase = "WAITING_FOR_FEEDBACK"
        self._emit("on_computer_guess", {
            "board": board,
            "guess": guess.to_color_names()
        })
        self._emit("on_waiting_for_feedback", {"board": board})

    def _process_round(self, session: _GameSession, guess: Code, result, board: int) -> None:
        if result.correct_position < 0 or result.correct_color < 0:
            raise RuntimeError("Invalid feedback: negative values are not allowed")

        max_pegs = self._config.variant.code_length if self._config else 0
        if result.correct_position + result.correct_color > max_pegs:
            raise RuntimeError("Invalid feedback: black + white exceeds code length")

        session.guess_provider.update(guess, result)
        session.rounds.append(Round(guess, result))

        self._emit("on_round_played", {
            "board": board,
            "round": len(session.rounds),
            "guess": guess.to_color_names(),
            "feedback": {
                "black": result.correct_position,
                "white": result.correct_color
            }
        })

        if not session.guess_provider.is_consistent():
            raise RuntimeError("Inconsistent feedback detected: no possible codes remain")

        if result.is_correct(max_pegs):
            session.state = GameState.WON
            self._phase = "AUTO_RUNNING"
            self._emit("on_game_won", {
                "board": board,
                "rounds": len(session.rounds)
            })
            return

        if len(session.rounds) >= self._max_rounds:
            session.state = GameState.LOST
            self._phase = "AUTO_RUNNING"
            self._emit("on_game_lost", {
                "board": board,
                "rounds": len(session.rounds)
            })

    def _step_spectator(self) -> None:
        for idx, session in enumerate(self._sessions, start=1):
            if self._session_is_running(session):
                self._run_single_round(session, idx)

    def _play_single(self, session: _GameSession, board: int) -> None:
        self._start_session(session)
        self._run_session_loop(session, board)

    def _play_parallel(self) -> None:
        for session in self._sessions:
            self._start_session(session)

        while any(self._session_is_running(s) for s in self._sessions):
            for idx, session in enumerate(self._sessions, start=1):
                if self._session_is_running(session):
                    self._run_single_round(session, idx)
            if self._config and self._config.delay_seconds > 0:
                time.sleep(self._config.delay_seconds)

    def _start_session(self, session: _GameSession) -> None:
        session.secret_code = session.secret_code_provider.create_secret_code()
        session.state = GameState.RUNNING
        self._build_view()

    def _session_is_running(self, session: _GameSession) -> bool:
        return session.state == GameState.RUNNING and len(session.rounds) < self._max_rounds

    def _run_session_loop(self, session: _GameSession, board: int) -> None:
        while self._session_is_running(session):
            self._run_single_round(session, board)
            if self._config and self._config.delay_seconds > 0 and not session.is_human_evaluator:
                time.sleep(self._config.delay_seconds)

    def _run_single_round(self, session: _GameSession, board: int) -> None:
        if not session.secret_code:
            raise RuntimeError("Secret code not available")
        if session.is_human_evaluator:
            if not session.pending_guess:
                self._produce_computer_guess(session, board)
            return

        guess = session.guess_provider.next_guess()
        result = session.evaluation_provider.evaluate(session.secret_code, guess)
        self._process_round(session, guess, result, board)
        self._build_view()

    def _emit(self, method: str, payload: Dict[str, Any]) -> None:
        if self._event_sink and hasattr(self._event_sink, method):
            getattr(self._event_sink, method)(payload)

    def _build_view(self) -> None:
        if not self._config:
            self._view = {}
            return
        boards = []
        for idx, session in enumerate(self._sessions, start=1):
            boards.append({
                "board": idx,
                "state": session.state.value,
                "rounds": [
                    {
                        "guess": round_.guess.to_color_names(),
                        "feedback": {
                            "black": round_.result.correct_position,
                            "white": round_.result.correct_color
                        }
                    } for round_ in session.rounds
                ],
                "secret_code": (
                    session.secret_code.to_color_names()
                    if session.secret_code and not session.evaluation_provider.uses_remote_secret()
                    else None
                )
            })
        round_count = max((len(session.rounds) for session in self._sessions), default=0)
        status = self._overall_status()
        board_a = boards[0]["rounds"] if boards else []
        board_b = boards[1]["rounds"] if len(boards) > 1 else []
        self._view = {
            "variant": {
                "name": self._config.variant.name,
                "code_length": self._config.variant.code_length,
                "color_count": self._config.variant.color_count
            },
            "mode": self._config.mode.value,
            "status": status,
            "round": round_count,
            "maxRounds": self._max_rounds,
            "boardA": board_a,
            "boardB": board_b,
            "phase": self._phase,
            "currentGuess": self._current_guess,
            "boards": boards
        }

    def _overall_status(self) -> str:
        if any(session.state == GameState.RUNNING for session in self._sessions):
            return GameState.RUNNING.value
        if self._sessions and all(session.state == GameState.WON for session in self._sessions):
            return GameState.WON.value
        if self._sessions and all(session.state == GameState.LOST for session in self._sessions):
            return GameState.LOST.value
        return GameState.NOT_STARTED.value
