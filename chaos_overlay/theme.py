"""Palette, polices et feuille de style Qt de l'interface (palette de la v2 conservée)."""

from __future__ import annotations

BACKGROUND = "#0f1923"
PANEL = "#1f2326"
ACCENT = "#ff4655"
ACCENT_HOVER = "#ff6b77"
TEXT = "#ece8e1"
MUTED = "#8b978f"
DIM = "#535c65"

# Police principale (Segoe UI sous Windows, Arial sinon).
FONT_FAMILY = "Segoe UI"
FONT_FALLBACKS = ["Segoe UI", "Arial", "Helvetica"]

STYLESHEET = f"""
QWidget#dashboard, QWidget#splash {{
    background-color: {BACKGROUND};
}}
QWidget {{
    color: {TEXT};
    font-size: 14px;
}}
QLabel#title {{
    font-size: 30px;
    font-weight: 800;
    letter-spacing: 2px;
}}
QLabel#subtitle {{
    color: {ACCENT};
    font-style: italic;
}}
QLabel#section {{
    color: {MUTED};
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
}}
QLabel#status {{
    color: {TEXT};
    font-weight: 700;
}}
QLabel#hint {{
    color: {DIM};
    font-size: 12px;
}}
QFrame#panel, QScrollArea#malusList, QWidget#malusRows {{
    background-color: {PANEL};
    border: none;
    border-radius: 8px;
}}
QComboBox, QSpinBox, QDoubleSpinBox {{
    background-color: {BACKGROUND};
    border: 1px solid {DIM};
    border-radius: 4px;
    padding: 4px 8px;
    min-height: 22px;
}}
QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {ACCENT};
}}
QComboBox QAbstractItemView {{
    background-color: {PANEL};
    selection-background-color: {ACCENT};
}}
QCheckBox {{
    font-weight: 700;
    spacing: 10px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {DIM};
    border-radius: 4px;
    background: {BACKGROUND};
}}
QCheckBox::indicator:checked {{
    background: {ACCENT};
    border-color: {ACCENT};
}}
QPushButton {{
    border: none;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 700;
    background-color: {PANEL};
    color: {MUTED};
}}
QPushButton:hover {{
    background-color: {DIM};
    color: {TEXT};
}}
QPushButton#primary {{
    background-color: {ACCENT};
    color: {TEXT};
    font-size: 18px;
    padding: 14px;
}}
QPushButton#primary:hover {{
    background-color: {ACCENT_HOVER};
}}
QPushButton#small {{
    padding: 4px 10px;
    font-size: 12px;
}}
QProgressBar {{
    background-color: {PANEL};
    border: none;
    border-radius: 5px;
    max-height: 10px;
}}
QProgressBar::chunk {{
    background-color: {ACCENT};
    border-radius: 5px;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 6px 2px 6px 0;
}}
QScrollBar::handle:vertical {{
    background: {DIM};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {MUTED};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    height: 0;
    background: none;
}}
QToolTip {{
    background-color: {PANEL};
    color: {TEXT};
    border: 1px solid {DIM};
}}
"""
