"""Low HP : les bords de l'écran rougissent et battent comme un cœur, comme à 1 PV."""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QRadialGradient

from chaos_overlay.malus.base import Malus, register

HEARTBEAT_MS = 1100
EDGE_COLOR = (200, 0, 20)


def heartbeat(elapsed_ms: int) -> float:
    """Intensité du battement (0,55 à 1) : un pic marqué au début de chaque battement."""
    phase = (elapsed_ms % HEARTBEAT_MS) / HEARTBEAT_MS
    return 0.55 + 0.45 * math.exp(-8 * phase) * (1 + math.cos(2 * math.pi * phase)) / 2


@register
class LowHp(Malus):
    key = "low_hp"
    label = "PV critiques"
    description = "Les bords de l'écran deviennent rouges et battent comme un cœur."
    default_duration_ms = 8000
    fade_in_ms = 400
    fade_out_ms = 600

    def paint(self, painter: QPainter, elapsed_ms: int) -> None:
        ctx = self.ctx
        center = QPointF(ctx.width / 2, ctx.height / 2)
        radius = math.hypot(ctx.width, ctx.height) / 2
        alpha = round(230 * heartbeat(elapsed_ms))
        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0.0, QColor(*EDGE_COLOR, 0))
        gradient.setColorAt(0.45, QColor(*EDGE_COLOR, 0))
        gradient.setColorAt(1.0, QColor(*EDGE_COLOR, alpha))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillRect(0, 0, ctx.width, ctx.height, gradient)
