"""HUD blocker : trois rectangles noirs sur des zones du HUD (haut gauche, bas droite, bas)."""

from __future__ import annotations

from chaos_overlay.malus.base import EffectContext, Malus, register


@register
class HudBlocker(Malus):
    key = "hud_blocker"
    default_duration_ms = 12000

    def _draw(self, ctx: EffectContext) -> None:
        w, h = ctx.width, ctx.height
        canvas = ctx.canvas
        # Haut gauche (minimap)
        self._track(canvas.create_rectangle(0, 0, w * 0.20, h * 0.30, fill="black", outline=""))
        # Bas droite
        self._track(canvas.create_rectangle(w * 0.75, h * 0.80, w, h, fill="black", outline=""))
        # Bas, entre 25 % et 45 % de la largeur
        self._track(canvas.create_rectangle(w * 0.25, h * 0.85, w * 0.45, h, fill="black", outline=""))
