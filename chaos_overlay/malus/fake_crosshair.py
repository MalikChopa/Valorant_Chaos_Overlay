"""Fake crosshair : une grande croix verte décalée du centre."""

from __future__ import annotations

from chaos_overlay.malus.base import EffectContext, Malus, register

COLOR = "#00ff00"
OFFSET_X = 45
OFFSET_Y = -40
ARM_LENGTH = 150
THICKNESS = 8


@register
class FakeCrosshair(Malus):
    key = "fake_crosshair"
    default_duration_ms = 10000

    def _draw(self, ctx: EffectContext) -> None:
        fx = (ctx.width // 2) + OFFSET_X
        fy = (ctx.height // 2) + OFFSET_Y
        size, thick = ARM_LENGTH, THICKNESS
        canvas = ctx.canvas
        # Barre horizontale puis barre verticale
        self._track(
            canvas.create_rectangle(fx - size, fy - thick // 2, fx + size, fy + thick // 2, fill=COLOR, outline="")
        )
        self._track(
            canvas.create_rectangle(fx - thick // 2, fy - size, fx + thick // 2, fy + size, fill=COLOR, outline="")
        )
