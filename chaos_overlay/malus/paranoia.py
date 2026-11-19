"""Paranoia : quatre faux pings d'ennemi (losange rouge + « !!! ») qui pulsent autour du centre."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPolygonF

from chaos_overlay import theme
from chaos_overlay.malus.base import Malus, register

PING_COUNT = 4
PING_SIZE = 15
PULSE_PERIOD_MS = 600


@register
class Paranoia(Malus):
    key = "paranoia"
    label = "Paranoïa"
    description = "Quatre faux pings d'ennemi apparaissent autour du viseur."
    default_duration_ms = 4000

    def setup(self) -> None:
        ctx, rng = self.ctx, self.ctx.rng
        self.pings: list[tuple[int, int]] = []
        for _ in range(PING_COUNT):
            # À gauche ou à droite du centre, jamais dessus : on doit tourner la tête.
            dx = rng.choice([rng.randint(-400, -100), rng.randint(100, 400)])
            dy = rng.randint(-300, 300)
            self.pings.append((ctx.width // 2 + round(dx * ctx.scale), ctx.height // 2 + round(dy * ctx.scale)))

    def paint(self, painter: QPainter, elapsed_ms: int) -> None:
        ctx = self.ctx
        pulse = 1.0 + 0.15 * math.sin(2 * math.pi * elapsed_ms / PULSE_PERIOD_MS)
        size = ctx.px(PING_SIZE) * pulse
        font = QFont(theme.FONT_FAMILY)
        font.setPixelSize(ctx.px(16))
        font.setBold(True)
        painter.setFont(font)
        for px, py in self.pings:
            diamond = QPolygonF(
                [QPointF(px, py - size), QPointF(px + size, py), QPointF(px, py + size), QPointF(px - size, py)]
            )
            painter.setPen(QPen(QColor("white"), 1))
            painter.setBrush(QColor(theme.ACCENT))
            painter.drawPolygon(diamond)
            painter.setPen(QColor(theme.ACCENT))
            painter.drawText(QPointF(px - ctx.px(12), py - ctx.px(24)), "!!!")
