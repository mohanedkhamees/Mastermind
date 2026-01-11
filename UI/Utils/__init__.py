# UI1/Utils/__init__.py
from UI.Utils.ColorMapper import (
    PEG_COLOR_MAP,
    PALETTE_SUPERHIRN,
    PALETTE_SUPERSUPERHIRN,
    color_to_peg
)
from UI.Utils.SettingsManager import SettingsManager, GameStatistics, GameHistoryEntry

__all__ = [
    'PEG_COLOR_MAP',
    'PALETTE_SUPERHIRN',
    'PALETTE_SUPERSUPERHIRN',
    'color_to_peg',
    'SettingsManager',
    'GameStatistics',
    'GameHistoryEntry'
]