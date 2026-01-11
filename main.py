# main.py
"""
SuperHirn - Mastermind Spiel
Entry Point für die Anwendung

Dies ist der Haupt-Einstiegspunkt für die Anwendung.
Für PyInstaller-Packaging optimiert.
"""
import sys
import os
from pathlib import Path

# Projekt-Root zum Python-Pfad hinzufügen
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# PyInstaller-Kompatibilität
# Wenn als Executable ausgeführt, Ressourcen-Pfad anpassen
if getattr(sys, 'frozen', False):
    # Executable-Modus: sys._MEIPASS enthält temporären Ordner mit allen Ressourcen
    # Projekt-Root bleibt für Imports wichtig
    base_path = Path(sys._MEIPASS)
    # Arbeitsverzeichnis auf temporären Ordner setzen (für Ressourcen)
    os.chdir(base_path)
else:
    # Script-Modus: Normaler Projekt-Root
    os.chdir(project_root)

# PySide6 Application importieren
from PySide6.QtWidgets import QApplication

# Application Layer Imports
from app.window import MainWindow
from app.styles import APP_QSS


def main():
    """
    Hauptfunktion - startet die SuperHirn-Anwendung
    
    Diese Funktion:
    1. Erstellt die QApplication
    2. Wendet das Styling an
    3. Erstellt und zeigt das Hauptfenster
    4. Startet die Event-Loop
    """
    # Qt Application erstellen
    app = QApplication(sys.argv)
    
    # Styling anwenden
    app.setStyleSheet(APP_QSS)
    
    # Hauptfenster erstellen und anzeigen
    window = MainWindow()
    window.show()
    
    # Event-Loop starten
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

