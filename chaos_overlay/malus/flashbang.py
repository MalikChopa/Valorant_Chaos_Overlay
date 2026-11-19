"""Flashbang : écran blanc qui aveugle d'un coup, puis s'estompe."""

from __future__ import annotations

from PySide6.QtGui import QColor, QPainter

from chaos_overlay.malus.base import Malus, register


@register
class Flashbang(Malus):
    key = "flashbang"
    label = "Flashbang"
    description = "Écran blanc aveuglant, qui s'estompe sur la fin."
    default_duration_ms = 2500
    fade_in_ms = 0  # comme une vraie flash : blanc immédiat
    fade_out_ms = 1500

    def paint(self, painter: QPainter, elapsed_ms: int) -> None:
        painter.fillRect(0, 0, self.ctx.width, self.ctx.height, QColor("white"))
