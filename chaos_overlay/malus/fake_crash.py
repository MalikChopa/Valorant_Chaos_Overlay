"""Fake crash : faux écran bleu d'erreur (un simple dessin : aucun lien avec le jeu ni l'anti-triche)."""

from __future__ import annotations

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QFont, QPainter

from chaos_overlay.malus.base import Malus, register

BACKGROUND = "#003399"
MESSAGE = "ANTI-CHEAT CRITICAL ERROR\nDisconnecting..."
FONT_SIZE = 28


@register
class FakeCrash(Malus):
    key = "fake_crash"
    label = "Faux crash"
    description = "Faux écran bleu d'erreur critique, le temps d'une frayeur."
    default_duration_ms = 2500
    fade_in_ms = 0  # un crash ne prévient pas
    fade_out_ms = 0

    def paint(self, painter: QPainter, elapsed_ms: int) -> None:
        ctx = self.ctx
        painter.fillRect(0, 0, ctx.width, ctx.height, QColor(BACKGROUND))
        font = QFont("Courier New")
        font.setPixelSize(ctx.px(FONT_SIZE * 4 / 3))  # 28 pt ≈ 37 px
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor("white"))
        painter.drawText(QRect(0, 0, ctx.width, ctx.height), Qt.AlignmentFlag.AlignCenter, MESSAGE)
