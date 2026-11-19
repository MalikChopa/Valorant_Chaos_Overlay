"""Mosquito : un carré noir de 15 px (en 1080p) qui rebondit sur les bords de l'écran."""

from __future__ import annotations

import random

from PySide6.QtGui import QColor, QPainter

from chaos_overlay.malus.base import Malus, register

SIZE = 15
TICK_MS = 30
START_SPEED = 25
SPEED_CHOICES = [-30, -15, 15, 30]
CHANGE_DIRECTION_CHANCE = 0.05


@register
class Mosquito(Malus):
    key = "mosquito"
    label = "Moustique"
    description = "Un petit carré noir qui vole partout sur l'écran."
    default_duration_ms = 10000
    fade_in_ms = 0
    fade_out_ms = 0

    def setup(self) -> None:
        # Hasard propre à l'instance : la trajectoire ne dépend que du tirage de départ.
        self.rng = random.Random(self.ctx.rng.random())
        self.x = self.ctx.width // 2
        self.y = self.ctx.height // 2
        self.dx = START_SPEED
        self.dy = START_SPEED
        self.ticks = 0

    def advance_to(self, elapsed_ms: int) -> None:
        """Fait avancer la simulation jusqu'à `elapsed_ms` (un pas toutes les 30 ms)."""
        size, scale = self.ctx.px(SIZE), self.ctx.scale
        while self.ticks < elapsed_ms // TICK_MS:
            self.ticks += 1
            self.x += round(self.dx * scale)
            self.y += round(self.dy * scale)
            if self.x <= 0 or self.x >= self.ctx.width - size:
                self.dx *= -1
            if self.y <= 0 or self.y >= self.ctx.height - size:
                self.dy *= -1
            self.x = max(0, min(self.ctx.width - size, self.x))
            self.y = max(0, min(self.ctx.height - size, self.y))
            if self.rng.random() < CHANGE_DIRECTION_CHANCE:
                self.dx, self.dy = self.rng.choice(SPEED_CHOICES), self.rng.choice(SPEED_CHOICES)

    def paint(self, painter: QPainter, elapsed_ms: int) -> None:
        self.advance_to(elapsed_ms)
        size = self.ctx.px(SIZE)
        painter.fillRect(self.x, self.y, size, size, QColor("black"))
