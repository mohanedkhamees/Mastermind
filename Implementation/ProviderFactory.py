from typing import Callable
from CoreDomainModel.AlgorithmType import AlgorithmType
from CoreDomainModel.GameConfig import GameConfig
from CoreDomainModel.GameMode import GameMode
from CoreDomainModel.GameVariant import GameVariant
from CoreDomainModel.ProviderFactory import IProviderFactory
from CoreDomainModel.IEvaluationProvider import IEvaluationProvider
from CoreDomainModel.IGuessProvider import IGuessProvider
from CoreDomainModel.ISecretCodeProvider import ISecretCodeProvider
from Implementation.Algorithms.ConsistencyBasedAlgorithm import ConsistencyBasedAlgorithm
from Implementation.Algorithms.KnuthAlgorithm import KnuthAlgorithm
from Implementation.EvaluationProviders.RemoteEvaluationProvider import RemoteEvaluationProvider
from Implementation.EvaluationProviders.SystemEvaluationProvider import SystemEvaluationProvider
from Implementation.EvaluationProviders.UIEvaluationProvider import UIEvaluationProvider
from Implementation.GuessProviders.AIGuessProvider import AIGuessProvider
from Implementation.GuessProviders.UIGuessProvider import UIGuessProvider
from Implementation.SecretCodeProviders.SystemSecretCodeProvider import SystemSecretCodeProvider
from Implementation.SecretCodeProviders.UISecretCodeProvider import UISecretCodeProvider
from Networking.NetworkService import NetworkService


class ProviderFactory(IProviderFactory):
    def __init__(self, network_service_factory: Callable[[str, str], NetworkService]):
        self._network_service_factory = network_service_factory

    def create_secret_code_provider(self, variant: GameVariant, config: GameConfig) -> ISecretCodeProvider:
        if config.mode == GameMode.KODIERER and config.kodierer_mode == "Mensch":
            return UISecretCodeProvider()
        return SystemSecretCodeProvider(variant)

    def create_evaluation_provider(self, variant: GameVariant, config: GameConfig) -> IEvaluationProvider:
        if config.mode == GameMode.RATER and config.rater_mode == "Online":
            return self._create_remote_eval_provider(variant, config)
        if config.mode == GameMode.KODIERER:
            if config.kodierer_mode == "Mensch":
                return UIEvaluationProvider()
            if config.kodierer_mode == "Codierer im Netz":
                return self._create_remote_eval_provider(variant, config, prefix="kodierer")
        return SystemEvaluationProvider()

    def create_guess_provider(
        self,
        variant: GameVariant,
        config: GameConfig,
        evaluation_provider: IEvaluationProvider,
        algorithm: AlgorithmType | None = None
    ) -> IGuessProvider:
        if config.mode == GameMode.RATER:
            return UIGuessProvider()

        algo = algorithm or config.algorithm
        eval_provider_for_algo = evaluation_provider
        if config.mode == GameMode.KODIERER and config.kodierer_mode == "Codierer im Netz":
            eval_provider_for_algo = SystemEvaluationProvider()

        if algo == AlgorithmType.KNUTH:
            algorithm_impl = KnuthAlgorithm(variant, eval_provider_for_algo)
        else:
            algorithm_impl = ConsistencyBasedAlgorithm(variant, eval_provider_for_algo)
        return AIGuessProvider(algorithm_impl)

    def _create_remote_eval_provider(
        self,
        variant: GameVariant,
        config: GameConfig,
        prefix: str = "rater"
    ) -> IEvaluationProvider:
        ip = config.raw.get(f"{prefix}_server_ip", "127.0.0.1")
        port = config.raw.get(f"{prefix}_server_port", 8080)
        gamer_id = config.raw.get(f"{prefix}_gamer_id", "player1")
        server_url = f"http://{ip}:{port}"
        network_service = self._network_service_factory(server_url, gamer_id)
        provider = RemoteEvaluationProvider(network_service, variant)
        if not provider.initialize():
            raise RuntimeError(f"Cannot connect to server: {server_url}")
        return provider
