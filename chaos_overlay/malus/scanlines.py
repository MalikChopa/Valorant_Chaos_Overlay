"""Scanlines : une bande noire de 4 px toutes les 8 px sur tout l'écran."""

from __future__ import annotations

from chaos_overlay.malus.base import EffectContext, Malus, register

LINE_HEIGHT = 4
LINE_SPACING = 8


@register
class Scanlines(Malus):
    key = "scanlines"
    default_duration_ms = 10000

    def _draw(self, ctx: EffectContext) -> None:
        for y in range(0, ctx.height, LINE_SPACING):
            self._track(ctx.canvas.create_rectangle(0, y, ctx.width, y + LINE_HEIGHT, fill="black", outline=""))
