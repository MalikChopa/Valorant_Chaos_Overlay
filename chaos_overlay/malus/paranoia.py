"""Paranoia : quatre faux pings d'ennemi (losange rouge + "!!!") autour du centre."""

from __future__ import annotations

from chaos_overlay import theme
from chaos_overlay.malus.base import EffectContext, Malus, register

PING_COUNT = 4


@register
class Paranoia(Malus):
    key = "paranoia"
    default_duration_ms = 4000

    def _draw(self, ctx: EffectContext) -> None:
        rng = ctx.rng
        canvas = ctx.canvas
        for _ in range(PING_COUNT):
            # Les deux tirages sont faits avant le choix, comme dans le code d'origine.
            left_offset = rng.randint(-400, -100)
            right_offset = rng.randint(100, 400)
            px = (ctx.width // 2) + rng.choice([left_offset, right_offset])
            py = (ctx.height // 2) + rng.randint(-300, 300)
            self._track(
                canvas.create_polygon(
                    px, py - 15, px + 15, py, px, py + 15, px - 15, py, fill=theme.ACCENT, outline="white"
                )
            )
            self._track(
                canvas.create_text(px, py - 30, text="!!!", fill=theme.ACCENT, font=(theme.FONT_FAMILY, 12, "bold"))
            )
