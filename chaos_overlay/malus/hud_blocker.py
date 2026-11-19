"""HUD blocker : des rectangles noirs sur les zones du HUD du profil de jeu choisi."""

from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPainter

from chaos_overlay.malus.base import Malus, register


@register
class HudBlocker(Malus):
    key = "hud_blocker"
    label = "HUD masqué"
    description = "Masque la minimap, la vie et les munitions (zones selon le profil de jeu)."
    default_duration_ms = 12000

    def paint(self, painter: QPainter, elapsed_ms: int) -> None:
        w, h = self.ctx.width, self.ctx.height
        for x0, y0, x1, y1 in self.ctx.profile.hud_zones:
            painter.fillRect(QRectF(x0 * w, y0 * h, (x1 - x0) * w, (y1 - y0) * h), QColor("black"))
