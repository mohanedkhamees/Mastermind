# app/styles.py
"""
Application Stylesheets
Enthält alle QSS-Styles für die Anwendung
"""

APP_QSS = """
QWidget {
    background: #0f0f14;
    color: #F3F3F6;
    font-family: Inter, Segoe UI, Arial;
}

QFrame#Card {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #14141c, stop:1 #0f0f14);
    border: 3px solid rgba(240, 240, 255, 0.65);
    border-radius: 18px;
}

QLabel#Title {
    font-size: 48px;
    font-weight: 800;
    letter-spacing: 2px;
}

QPushButton { border: none; }

QPushButton#Chip {
    background: rgba(220, 220, 235, 0.18);
    color: rgba(245,245,255,0.85);
    border: 1px solid rgba(255,255,255,0.12);
    padding: 8px 14px;
    border-radius: 14px;
}

QPushButton#Chip:checked {
    background: rgba(220, 210, 255, 0.90);
    color: rgba(30, 25, 45, 1.0);
    border: 1px solid rgba(255,255,255,0.20);
}

QPushButton#Primary {
    background: rgba(170, 150, 255, 0.75);
    color: rgba(20, 18, 30, 1.0);
    border: 1px solid rgba(255,255,255,0.20);
    padding: 10px 16px;
    border-radius: 16px;
}

QPushButton#Primary:pressed { background: rgba(170, 150, 255, 0.60); }
QPushButton#Primary:disabled { 
    background: rgba(100, 100, 120, 0.4);
    color: rgba(150, 150, 150, 0.6);
}

QPushButton#Ghost {
    background: rgba(255,255,255,0.06);
    color: rgba(245,245,255,0.85);
    border: 1px solid rgba(255,255,255,0.12);
    padding: 10px 16px;
    border-radius: 16px;
}

QPushButton#Ghost:pressed { background: rgba(255,255,255,0.10); }

QMessageBox {
    background: #0f0f14;
    color: #F3F3F6;
}

/* Custom Titlebar */
QWidget#TitleBar {
    background: #0f0f14;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

QPushButton#TitleButton {
    background: transparent;
    border: none;
    padding: 8px 16px;
    color: rgba(245, 245, 255, 0.8);
    font-size: 12px;
}

QPushButton#TitleButton:hover {
    background: rgba(255, 255, 255, 0.1);
    color: rgba(245, 245, 255, 1.0);
}

QPushButton#TitleButton#CloseButton:hover {
    background: rgba(220, 50, 50, 0.8);
    color: white;
}
"""
