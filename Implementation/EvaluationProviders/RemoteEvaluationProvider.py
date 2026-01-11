# Implementation/EvaluationProviders/RemoteEvaluationProvider.py
from typing import Optional
from CoreDomainModel.IEvaluationProvider import IEvaluationProvider
from CoreDomainModel.EvaluationResult import EvaluationResult
from CoreDomainModel.Code import Code
from CoreDomainModel.GameVariant import GameVariant
from Networking.NetworkService import NetworkService


class RemoteEvaluationProvider(IEvaluationProvider):
    """
    Evaluation provider that uses remote server for evaluation
    Server creates and stores the secret code
    """

    def __init__(self, network_service: NetworkService, variant: GameVariant):
        self._network_service = network_service
        self._variant = variant
        self._game_id: Optional[int] = None
        self._initialized = False

    def initialize(self) -> bool:
        """
        Initialize connection - server creates secret code
        Returns False if server is not available
        """
        self._game_id = self._network_service.start_remote_game(self._variant)
        self._initialized = (self._game_id is not None)
        return self._initialized

    def get_game_id(self) -> Optional[int]:
        """Get current game ID"""
        return self._game_id

    def evaluate(self, secret: Code, guess: Code) -> EvaluationResult:
        """
        Evaluate guess - secret is on server, we only send guess
        Note: secret parameter is required by interface but not used in online mode
        """
        if not self._initialized:
            raise RuntimeError("RemoteEvaluationProvider not initialized")

        result = self._network_service.evaluate_guess(guess)

        if result is None:
            raise RuntimeError("Server evaluation failed")

        return result

    def uses_remote_secret(self) -> bool:
        return True

    def set_feedback(self, black: int, white: int) -> None:
        pass
