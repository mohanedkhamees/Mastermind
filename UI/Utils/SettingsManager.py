# UI1/Utils/SettingsManager.py
import json
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class GameStatistics:
    games_played: int = 0
    games_won: int = 0
    total_rounds: int = 0
    best_score: int = 999

    @property
    def win_rate(self) -> float:
        if self.games_played == 0:
            return 0.0
        return (self.games_won / self.games_played) * 100

    @property
    def avg_rounds(self) -> float:
        if self.games_played == 0:
            return 0.0
        return self.total_rounds / self.games_played


@dataclass
class GameHistoryEntry:
    mode: str
    variant: str
    won: bool
    rounds: int
    timestamp: str


class SettingsManager:
    SETTINGS_FILE = Path.home() / ".superhirn_settings.json"
    STATS_FILE = Path.home() / ".superhirn_stats.json"
    HISTORY_FILE = Path.home() / ".superhirn_history.json"

    @staticmethod
    def load_settings() -> Dict:
        if SettingsManager.SETTINGS_FILE.exists():
            try:
                with open(SettingsManager.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"default_variant": "SUPERHIRN", "default_mode": "RATER"}

    @staticmethod
    def save_settings(settings: Dict):
        with open(SettingsManager.SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)

    @staticmethod
    def load_stats() -> GameStatistics:
        if SettingsManager.STATS_FILE.exists():
            try:
                with open(SettingsManager.STATS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return GameStatistics(**data)
            except:
                pass
        return GameStatistics()

    @staticmethod
    def save_stats(stats: GameStatistics):
        with open(SettingsManager.STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(asdict(stats), f, indent=2)

    @staticmethod
    def load_history() -> List[GameHistoryEntry]:
        if SettingsManager.HISTORY_FILE.exists():
            try:
                with open(SettingsManager.HISTORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [GameHistoryEntry(**entry) for entry in data]
            except:
                pass
        return []

    @staticmethod
    def save_history(history: List[GameHistoryEntry]):
        with open(SettingsManager.HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump([asdict(entry) for entry in history], f, indent=2)

    @staticmethod
    def add_history_entry(entry: GameHistoryEntry):
        history = SettingsManager.load_history()
        history.append(entry)
        if len(history) > 100:  # Keep last 100 games
            history = history[-100:]
        SettingsManager.save_history(history)