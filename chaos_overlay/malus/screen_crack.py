"""Screen crack : 15 fissures grises qui partent d'un point tiré au hasard."""

from __future__ import annotations

from chaos_overlay.malus.base import EffectContext, Malus, register

COLOR = "#e0e0e0"
CRACK_COUNT = 15


@register
class ScreenCrack(Malus):
    key = "screen_crack"
    default_duration_ms = 8000

    def _draw(self, ctx: EffectContext) -> None:
        rng = ctx.rng
        start_x = rng.randint(300, ctx.width - 300)
        start_y = rng.randint(200, ctx.height - 200)
        for _ in range(CRACK_COUNT):
            x, y = start_x, start_y
            coords = [start_x, start_y]
            for _ in range(rng.randint(3, 5)):
                x += rng.randint(-400, 400)
                y += rng.randint(-400, 400)
                coords.extend([x, y])
            # Tkinter accepte la liste de coordonnées telle quelle (même rendu que *coords).
            self._track(ctx.canvas.create_line(coords, fill=COLOR, width=rng.randint(1, 3)))
