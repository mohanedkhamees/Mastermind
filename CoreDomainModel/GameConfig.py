from dataclasses import dataclass
from typing import Any, Dict
from CoreDomainModel.AlgorithmType import AlgorithmType
from CoreDomainModel.GameMode import GameMode
from CoreDomainModel.GameVariant import GameVariant


@dataclass(frozen=True)
class GameConfig:
    raw: Dict[str, Any]
    variant: GameVariant
    mode: GameMode
    algorithm: AlgorithmType
    algorithm1: AlgorithmType
    algorithm2: AlgorithmType
    delay_seconds: int
    rater_mode: str
    kodierer_mode: str
