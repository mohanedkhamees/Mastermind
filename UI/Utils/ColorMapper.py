# UI1/Utils/ColorMapper.py
from typing import Dict
from PySide6.QtGui import QColor

# Color mapping from color names to QColor
PEG_COLOR_MAP: Dict[str, QColor] = {
    "RED": QColor("#e53935"),
    "ORANGE": QColor("#fb8c00"),
    "YELLOW": QColor("#fdd835"),
    "GREEN": QColor("#43a047"),
    "BLUE": QColor("#1e88e5"),
    "BROWN": QColor("#6d4c41"),
    "WHITE": QColor("#ffffff"),
    "BLACK": QColor("#000000"),
}

# UI1 Color Palettes
# Farbkodierung: 1=Rot, 2=Grün, 3=Gelb, 4=Blau, 5=Orange, 6=Braun, 7=Weiss, 8=Schwarz
PALETTE_SUPERHIRN = [
    QColor("#e53935"),  # 1=Rot
    QColor("#43a047"),  # 2=Grün
    QColor("#fdd835"),  # 3=Gelb
    QColor("#1e88e5"),  # 4=Blau
    QColor("#fb8c00"),  # 5=Orange
    QColor("#6d4c41"),  # 6=Braun
]

PALETTE_SUPERSUPERHIRN = [
    QColor("#e53935"),  # 1=Rot
    QColor("#43a047"),  # 2=Grün
    QColor("#fdd835"),  # 3=Gelb
    QColor("#1e88e5"),  # 4=Blau
    QColor("#fb8c00"),  # 5=Orange
    QColor("#6d4c41"),  # 6=Braun
    QColor("#ffffff"),  # 7=Weiss
    QColor("#000000"),  # 8=Schwarz
]


def color_to_name(color: QColor) -> str:
    """Convert QColor to color name based on RGB values"""
    rgb = (color.red(), color.green(), color.blue())

    color_map = {
        (229, 57, 53): "RED",
        (67, 160, 71): "GREEN",
        (253, 216, 53): "YELLOW",
        (30, 136, 229): "BLUE",
        (251, 140, 0): "ORANGE",
        (109, 76, 65): "BROWN",
        (255, 255, 255): "WHITE",
        (0, 0, 0): "BLACK",
        (0, 172, 193): "BLUE",
        (142, 36, 170): "BLUE",
    }

    if rgb in color_map:
        return color_map[rgb]

    # Fallback: find closest color by RGB distance
    min_dist = float('inf')
    closest = "RED"
    for (r, g, b), peg in color_map.items():
        dist = ((r - rgb[0]) ** 2 + (g - rgb[1]) ** 2 + (b - rgb[2]) ** 2) ** 0.5
        if dist < min_dist:
            min_dist = dist
            closest = peg

    return closest
