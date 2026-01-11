from ApplicationControl.GameController import GameController
from ApplicationControl.DelaySynchronizer import DelaySynchronizer


class MultiGameController:
    """
    Controls exactly two games, each with its own algorithm.
    Used for direct comparison of strategies.
    """

    def __init__(
        self,
        game1: GameController,
        game2: GameController,
        delay: DelaySynchronizer | None = None
    ):
        self._game1 = game1
        self._game2 = game2
        self._delay = delay

    def play(self):
        print("\n===== GAME 1 =====")
        self._game1.start_game()
        if self._delay:
            self._game1.play(delay=self._delay)
        else:
            self._game1.play()

        print("\n===== GAME 2 =====")
        self._game2.start_game()
        if self._delay:
            self._game2.play(delay=self._delay)
        else:
            self._game2.play()
