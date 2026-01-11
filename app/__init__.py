# app/__init__.py
"""
Application Layer
Enthält Window-Management, Styles und Application-Konfiguration
"""

from app.window import MainWindow, TitleBar
from app.styles import APP_QSS

__all__ = ['MainWindow', 'TitleBar', 'APP_QSS']
