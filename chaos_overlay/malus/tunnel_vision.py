"""Tunnel vision : tout est noir sauf un carré au centre (600 px en 1080p)."""

from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPainter, QPainterPath

from chaos_overlay.malus.base import Malus, register

HALF_SIZE = 300


@register
class TunnelVision(Malus):
    key = "tunnel_vision"
    label = "Vision tunnel"
    description = "Tout l'écran est noir, sauf un carré au centre."
    default_duration_ms = 8000

    def paint(self, painter: QPainter, elapsed_ms: int) -> None:
        ctx = self.ctx
        r = ctx.px(HALF_SIZE)
        cx, cy = ctx.width // 2, ctx.height // 2
        path = QPainterPath()
        path.addRect(QRectF(0, 0, ctx.width, ctx.height))
        path.addRect(QRectF(cx - r, cy - r, 2 * r, 2 * r))  # règle pair-impair : le carré devient un trou
        painter.fillPath(path, QColor("black"))
