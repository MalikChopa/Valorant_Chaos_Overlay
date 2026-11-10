"""Tunnel vision : tout est noir sauf un carré de 600 px au centre."""

from __future__ import annotations

from chaos_overlay.malus.base import EffectContext, Malus, register

HALF_SIZE = 300


@register
class TunnelVision(Malus):
    key = "tunnel_vision"
    default_duration_ms = 8000

    def _draw(self, ctx: EffectContext) -> None:
        cx, cy, r = ctx.width // 2, ctx.height // 2, HALF_SIZE
        canvas = ctx.canvas
        self._track(canvas.create_rectangle(0, 0, ctx.width, cy - r, fill="black", outline=""))
        self._track(canvas.create_rectangle(0, cy + r, ctx.width, ctx.height, fill="black", outline=""))
        self._track(canvas.create_rectangle(0, cy - r, cx - r, cy + r, fill="black", outline=""))
        self._track(canvas.create_rectangle(cx + r, cy - r, ctx.width, cy + r, fill="black", outline=""))
