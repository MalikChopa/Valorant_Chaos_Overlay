"""Fake crosshair : une grande croix verte décalée du centre."""

from __future__ import annotations

from PySide6.QtGui import QColor, QPainter

from chaos_overlay.malus.base import Malus, register

COLOR = "#00ff00"
OFFSET_X = 45
OFFSET_Y = -40
ARM_LENGTH = 150
THICKNESS = 8


@register
class FakeCrosshair(Malus):
    key = "fake_crosshair"
    label = "Faux viseur"
    description = "Une grande croix verte, décalée du vrai centre."
    default_duration_ms = 10000

    def paint(self, painter: QPainter, elapsed_ms: int) -> None:
        ctx = self.ctx
        fx = ctx.width // 2 + round(OFFSET_X * ctx.scale)
        fy = ctx.height // 2 + round(OFFSET_Y * ctx.scale)
        size, thick = ctx.px(ARM_LENGTH), ctx.px(THICKNESS)
        color = QColor(COLOR)
        painter.fillRect(fx - size, fy - thick // 2, 2 * size, thick, color)  # barre horizontale
        painter.fillRect(fx - thick // 2, fy - size, thick, 2 * size, color)  # barre verticale
