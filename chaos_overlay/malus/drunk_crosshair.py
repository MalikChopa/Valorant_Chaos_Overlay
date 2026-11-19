"""Drunk crosshair : un faux viseur qui dérive autour du centre, comme après une soirée de trop."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPainter, QPen

from chaos_overlay.malus.base import Malus, register

COLOR = "#00ffcc"
AMPLITUDE = 110  # px en 1080p
PERIOD_X_MS = 2300
PERIOD_Y_MS = 1700
ARM = 12
GAP = 6


@register
class DrunkCrosshair(Malus):
    key = "drunk_crosshair"
    label = "Viseur ivre"
    description = "Un faux viseur qui tangue autour du centre de l'écran."
    default_duration_ms = 10000

    def setup(self) -> None:
        # Point de départ différent à chaque fois.
        self.phase = self.ctx.rng.uniform(0, 2 * math.pi)

    def position(self, elapsed_ms: int) -> QPointF:
        """Courbe de Lissajous autour du centre (périodes différentes en x et en y)."""
        ctx = self.ctx
        amplitude = AMPLITUDE * ctx.scale
        x = ctx.width / 2 + amplitude * math.sin(2 * math.pi * elapsed_ms / PERIOD_X_MS + self.phase)
        y = ctx.height / 2 + amplitude * 0.7 * math.sin(2 * math.pi * elapsed_ms / PERIOD_Y_MS + 2 * self.phase)
        return QPointF(x, y)

    def paint(self, painter: QPainter, elapsed_ms: int) -> None:
        ctx = self.ctx
        p = self.position(elapsed_ms)
        arm, gap = ctx.px(ARM), ctx.px(GAP)
        painter.setPen(QPen(QColor(COLOR), ctx.px(3)))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            painter.drawLine(
                QPointF(p.x() + dx * gap, p.y() + dy * gap), QPointF(p.x() + dx * (gap + arm), p.y() + dy * (gap + arm))
            )
        painter.setBrush(QColor(COLOR))
        painter.drawEllipse(p, ctx.px(2), ctx.px(2))
