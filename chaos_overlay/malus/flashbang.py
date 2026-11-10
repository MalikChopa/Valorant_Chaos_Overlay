"""Flashbang : écran blanc pendant 2,5 s."""

from __future__ import annotations

from chaos_overlay.malus.base import EffectContext, Malus, register


@register
class Flashbang(Malus):
    key = "flashbang"
    default_duration_ms = 2500

    def _draw(self, ctx: EffectContext) -> None:
        self._track(ctx.canvas.create_rectangle(0, 0, ctx.width, ctx.height, fill="white", outline=""))
