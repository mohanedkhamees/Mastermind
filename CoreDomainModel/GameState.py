# GameState.py
from enum import Enum


class GameState(Enum):
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    WON = "WON"
    LOST = "LOST"
