"""Screen crack : 15 fissures grises qui partent d'un point tiré au hasard."""

from __future__ import annotations

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QPen

from chaos_overlay.malus.base import Malus, register

COLOR = "#e0e0e0"
CRACK_COUNT = 15
MARGIN_X = 300
MARGIN_Y = 200
STEP = 400


@register
class ScreenCrack(Malus):
    key = "screen_crack"
    label = "Écran fissuré"
    description = "L'écran se fissure à partir d'un point au hasard."
    default_duration_ms = 8000

    def setup(self) -> None:
        ctx, rng = self.ctx, self.ctx.rng
        margin_x = min(ctx.px(MARGIN_X), ctx.width // 2)
        margin_y = min(ctx.px(MARGIN_Y), ctx.height // 2)
        start = QPointF(rng.randint(margin_x, ctx.width - margin_x), rng.randint(margin_y, ctx.height - margin_y))
        step = ctx.px(STEP)
        self.cracks: list[tuple[list[QPointF], int]] = []
        for _ in range(CRACK_COUNT):
            point = start
            points = [point]
            for _ in range(rng.randint(3, 5)):
                point = QPointF(point.x() + rng.randint(-step, step), point.y() + rng.randint(-step, step))
                points.append(point)
            self.cracks.append((points, rng.randint(1, 3)))

    def paint(self, painter: QPainter, elapsed_ms: int) -> None:
        color = QColor(COLOR)
        for points, width in self.cracks:
            pen = QPen(color, self.ctx.px(width))
            pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
            painter.setPen(pen)
            painter.drawPolyline(points)
