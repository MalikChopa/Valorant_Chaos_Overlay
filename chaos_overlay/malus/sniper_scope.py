"""Sniper scope : l'écran devient une lunette de sniper qui tangue légèrement."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen

from chaos_overlay.malus.base import Malus, register

RADIUS_RATIO = 0.42  # rayon de la lunette, en fraction de la hauteur de l'écran
SWAY = 25  # amplitude du tangage (px en 1080p)
SWAY_PERIOD_MS = 2600


@register
class SniperScope(Malus):
    key = "sniper_scope"
    label = "Lunette de sniper"
    description = "Vue à travers une lunette qui tangue : tout le reste est noir."
    default_duration_ms = 8000
    fade_in_ms = 250

    def center(self, elapsed_ms: int) -> QPointF:
        """Centre de la lunette : une petite courbe en huit autour du milieu de l'écran."""
        ctx = self.ctx
        phase = 2 * math.pi * elapsed_ms / SWAY_PERIOD_MS
        sway = SWAY * ctx.scale
        return QPointF(ctx.width / 2 + sway * math.sin(phase), ctx.height / 2 + sway * 0.5 * math.sin(2 * phase))

    def paint(self, painter: QPainter, elapsed_ms: int) -> None:
        ctx = self.ctx
        c = self.center(elapsed_ms)
        radius = RADIUS_RATIO * ctx.height
        path = QPainterPath()
        path.addRect(QRectF(0, 0, ctx.width, ctx.height))
        path.addEllipse(c, radius, radius)
        black = QColor("black")
        painter.fillPath(path, black)

        # Réticule fin et bord de la lunette.
        painter.setPen(QPen(black, ctx.px(2)))
        painter.drawLine(QPointF(c.x() - radius, c.y()), QPointF(c.x() + radius, c.y()))
        painter.drawLine(QPointF(c.x(), c.y() - radius), QPointF(c.x(), c.y() + radius))
        painter.setPen(QPen(black, ctx.px(12)))
        painter.drawEllipse(c, radius, radius)
