from abc import ABC, abstractmethod
from CoreDomainModel.GameConfig import GameConfig
from CoreDomainModel.AlgorithmType import AlgorithmType
from CoreDomainModel.GameVariant import GameVariant
from CoreDomainModel.IEvaluationProvider import IEvaluationProvider
from CoreDomainModel.IGuessProvider import IGuessProvider
from CoreDomainModel.ISecretCodeProvider import ISecretCodeProvider


class IProviderFactory(ABC):

    @abstractmethod
    def create_secret_code_provider(self, variant: GameVariant, config: GameConfig) -> ISecretCodeProvider:
        pass

    @abstractmethod
    def create_evaluation_provider(self, variant: GameVariant, config: GameConfig) -> IEvaluationProvider:
        pass

    @abstractmethod
    def create_guess_provider(
        self,
        variant: GameVariant,
        config: GameConfig,
        evaluation_provider: IEvaluationProvider,
        algorithm: AlgorithmType | None = None
    ) -> IGuessProvider:
        pass
