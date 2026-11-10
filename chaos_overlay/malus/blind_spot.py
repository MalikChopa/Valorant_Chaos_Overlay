"""Blind spot : un disque noir de 160 px au centre de l'écran."""

from __future__ import annotations

from chaos_overlay import theme
from chaos_overlay.malus.base import EffectContext, Malus, register

RADIUS = 80


@register
class BlindSpot(Malus):
    key = "blind_spot"
    default_duration_ms = 8000

    def _draw(self, ctx: EffectContext) -> None:
        cx, cy = ctx.width // 2, ctx.height // 2
        self._track(
            ctx.canvas.create_oval(
                cx - RADIUS, cy - RADIUS, cx + RADIUS, cy + RADIUS, fill="black", outline=theme.ACCENT, width=2
            )
        )
