"""Scanlines : une bande noire de 4 px toutes les 8 px (en 1080p) sur tout l'écran."""

from __future__ import annotations

from PySide6.QtGui import QColor, QPainter

from chaos_overlay.malus.base import Malus, register

LINE_HEIGHT = 4
LINE_SPACING = 8


@register
class Scanlines(Malus):
    key = "scanlines"
    label = "Scanlines"
    description = "Des bandes noires horizontales, comme un vieil écran."
    default_duration_ms = 10000

    def paint(self, painter: QPainter, elapsed_ms: int) -> None:
        ctx = self.ctx
        line, spacing = ctx.px(LINE_HEIGHT), max(ctx.px(LINE_SPACING), ctx.px(LINE_HEIGHT) + 1)
        black = QColor("black")
        for y in range(0, ctx.height, spacing):
            painter.fillRect(0, y, ctx.width, line, black)
