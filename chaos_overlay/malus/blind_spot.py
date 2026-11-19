"""Blind spot : un disque noir au centre de l'écran (160 px en 1080p)."""

from __future__ import annotations

from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPainter, QPen

from chaos_overlay import theme
from chaos_overlay.malus.base import Malus, register

RADIUS = 80


@register
class BlindSpot(Malus):
    key = "blind_spot"
    label = "Angle mort"
    description = "Un disque noir cache le centre de l'écran."
    default_duration_ms = 8000

    def paint(self, painter: QPainter, elapsed_ms: int) -> None:
        ctx = self.ctx
        radius = ctx.px(RADIUS)
        painter.setPen(QPen(QColor(theme.ACCENT), ctx.px(2)))
        painter.setBrush(QColor("black"))
        painter.drawEllipse(QPointF(ctx.width / 2, ctx.height / 2), radius, radius)
