from CoreDomainModel.Game import Game
from CoreDomainModel.GameState import GameState
from CoreDomainModel.Round import Round
from CoreDomainModel.IGuessProvider import IGuessProvider
from CoreDomainModel.IEvaluationProvider import IEvaluationProvider
from CoreDomainModel.ISecretCodeProvider import ISecretCodeProvider


class GameController:
    """
    Central orchestrator of a single Superhirn game.
    Coordinates guessing, evaluation and game state.
    """

    def __init__(
        self,
        game: Game,
        guess_provider: IGuessProvider,
        evaluation_provider: IEvaluationProvider,
        secret_code_provider: ISecretCodeProvider
    ):
        self._listeners = []
        self._game = game
        self._guess_provider = guess_provider
        self._evaluation_provider = evaluation_provider
        self._secret_code_provider = secret_code_provider
        self._secret_code = None

    # -------------------------------------------------
    # GAME START
    # -------------------------------------------------
    def add_listener(self, listener):
        self._listeners.append(listener)

    def _notify_round(self, guess, result):
        for l in self._listeners:
            l.on_round_played(guess, result)

    def _notify_win(self):
        for l in self._listeners:
            l.on_game_won()

    def _notify_loss(self):
        for l in self._listeners:
            l.on_game_lost()

    def start_game(self):
        self._secret_code = self._secret_code_provider.create_secret_code()
        self._game.start()

    # -------------------------------------------------
    # GAME LOOP
    # -------------------------------------------------

    def play(self, delay=None):
        if self._game.get_state() != GameState.RUNNING:
            raise RuntimeError("Game must be started before playing")

        variant = self._game.get_variant()
        max_pegs = variant.code_length

        while (
            self._game.get_state() == GameState.RUNNING
            and self._game.has_rounds_left()
        ):
            # Optional delay (Computer vs Computer)
            if delay:
                delay.wait()

            # 1. Get next guess
            guess = self._guess_provider.next_guess()

            print("\n--- Computer Guess ---")
            print(f"Guess: {guess.get_pegs()}")

            # 2. Evaluate guess
            result = self._evaluation_provider.evaluate(self._secret_code, guess)

            # 3. Validate feedback (logical checks)
            if result.correct_position < 0 or result.correct_color < 0:
                raise RuntimeError("Invalid feedback: negative values are not allowed")

            if result.correct_position + result.correct_color > max_pegs:
                raise RuntimeError(
                    "Invalid feedback: black + white exceeds code length"
                )

            # 4. Update algorithm / guess provider
            self._guess_provider.update(guess, result)

            # 5. Store round
            self._game.add_round(Round(guess, result))
            self._notify_round(guess, result)

            print(
                f"Feedback: black={result.correct_position}, "
                f"white={result.correct_color}"
            )

            # 6. Check for inconsistent feedback
            if not self._guess_provider.is_consistent():
                raise RuntimeError(
                    "Inconsistent feedback detected: no possible codes remain"
                )

            # 7. Win condition
            if result.is_correct(max_pegs):
                print("🎉 Game WON!")
                self._game._state = GameState.WON
                self._notify_win()

                return

        # -------------------------------------------------
        # LOSS CONDITION
        # -------------------------------------------------

        if not self._game.has_rounds_left():
            print("❌ Game LOST: maximum number of guesses reached")
            self._game._state = GameState.LOST
            self._notify_loss()

