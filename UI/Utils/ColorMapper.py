# UI1/Utils/ColorMapper.py
from typing import Dict
from CoreDomainModel.PegColor import PegColor
from PySide6.QtGui import QColor

# Color mapping from PegColor to QColor
PEG_COLOR_MAP: Dict[PegColor, QColor] = {
    PegColor.RED: QColor("#e53935"),
    PegColor.ORANGE: QColor("#fb8c00"),
    PegColor.YELLOW: QColor("#fdd835"),
    PegColor.GREEN: QColor("#43a047"),
    PegColor.BLUE: QColor("#1e88e5"),
    PegColor.BROWN: QColor("#6d4c41"),
    PegColor.WHITE: QColor("#ffffff"),
    PegColor.BLACK: QColor("#000000"),
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


def color_to_peg(color: QColor) -> PegColor:
    """Convert QColor to PegColor based on RGB values"""
    rgb = (color.red(), color.green(), color.blue())

    color_map = {
        (229, 57, 53): PegColor.RED,  # #e53935 - 1=Rot
        (67, 160, 71): PegColor.GREEN,  # #43a047 - 2=Grün
        (253, 216, 53): PegColor.YELLOW,  # #fdd835 - 3=Gelb
        (30, 136, 229): PegColor.BLUE,  # #1e88e5 - 4=Blau
        (251, 140, 0): PegColor.ORANGE,  # #fb8c00 - 5=Orange
        (109, 76, 65): PegColor.BROWN,  # #6d4c41 - 6=Braun
        (255, 255, 255): PegColor.WHITE,  # #ffffff - 7=Weiss
        (0, 0, 0): PegColor.BLACK,  # #000000 - 8=Schwarz
        (0, 172, 193): PegColor.BLUE,  # #00acc1 (cyan -> blue)
        (142, 36, 170): PegColor.BLUE,  # #8e24aa (purple -> blue)
    }

    if rgb in color_map:
        return color_map[rgb]

    # Fallback: find closest color by RGB distance
    min_dist = float('inf')
    closest = PegColor.RED
    for (r, g, b), peg in color_map.items():
        dist = ((r - rgb[0]) ** 2 + (g - rgb[1]) ** 2 + (b - rgb[2]) ** 2) ** 0.5
        if dist < min_dist:
            min_dist = dist
            closest = peg

    return closest