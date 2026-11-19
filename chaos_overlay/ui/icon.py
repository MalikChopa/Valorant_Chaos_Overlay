"""Icône de l'appli, dessinée en code (aucun fichier image à embarquer pour la fenêtre et la zone de notification).

Un losange « ping » rouge sur un carré arrondi sombre, aux couleurs de la palette.
`scripts/make_icon.py` s'en sert pour produire `assets/chaos_overlay.ico` (icône de l'exe).
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QImage, QPainter, QPen, QPixmap, QPolygonF

from chaos_overlay import theme

SIZES = (16, 24, 32, 48, 64, 128, 256)


def render_icon(size: int, paused: bool = False) -> QImage:
    """Icône carrée de `size` px ; `paused` la grise (chaos en pause)."""
    image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(theme.BACKGROUND))
    painter.drawRoundedRect(QRectF(0, 0, size, size), size * 0.22, size * 0.22)

    accent = QColor(theme.DIM if paused else theme.ACCENT)
    c, r = size / 2, size * 0.32
    diamond = QPolygonF([QPointF(c, c - r), QPointF(c + r, c), QPointF(c, c + r), QPointF(c - r, c)])
    painter.setBrush(accent)
    painter.setPen(QPen(QColor(theme.TEXT), max(1.0, size / 20)))
    painter.drawPolygon(diamond)
    painter.end()
    return image


def app_icon(paused: bool = False) -> QIcon:
    """QIcon à plusieurs tailles, pour les fenêtres et la zone de notification."""
    icon = QIcon()
    for size in SIZES:
        icon.addPixmap(QPixmap.fromImage(render_icon(size, paused)))
    return icon
