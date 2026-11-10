"""Mosquito : un carré noir de 15 px qui rebondit sur les bords de l'écran."""

from __future__ import annotations

from chaos_overlay.malus.base import EffectContext, Malus, register

SIZE = 15
TICK_MS = 30
START_SPEED = 25
SPEED_CHOICES = [-30, -15, 15, 30]
CHANGE_DIRECTION_CHANCE = 0.05


@register
class Mosquito(Malus):
    key = "mosquito"
    default_duration_ms = 10000

    def __init__(self, duration_ms: int | None = None) -> None:
        super().__init__(duration_ms)
        # Position, vitesse et carré propres à cette instance (plus d'état partagé).
        self.x = 0
        self.y = 0
        self.dx = START_SPEED
        self.dy = START_SPEED
        self.square = 0

    def _draw(self, ctx: EffectContext) -> None:
        self.x, self.y = ctx.width // 2, ctx.height // 2
        self.square = self._track(
            ctx.canvas.create_rectangle(self.x, self.y, self.x + SIZE, self.y + SIZE, fill="black", outline="")
        )
        self._move(ctx)

    def _move(self, ctx: EffectContext) -> None:
        """Avance d'un pas, rebondit sur les bords, change parfois de direction, puis se reprogramme."""
        self.x += self.dx
        self.y += self.dy
        if self.x <= 0 or self.x >= ctx.width - SIZE:
            self.dx *= -1
        if self.y <= 0 or self.y >= ctx.height - SIZE:
            self.dy *= -1
        if ctx.rng.random() < CHANGE_DIRECTION_CHANCE:
            self.dx, self.dy = ctx.rng.choice(SPEED_CHOICES), ctx.rng.choice(SPEED_CHOICES)
        ctx.canvas.coords(self.square, self.x, self.y, self.x + SIZE, self.y + SIZE)
        self._schedule(TICK_MS, lambda: self._move(ctx))
