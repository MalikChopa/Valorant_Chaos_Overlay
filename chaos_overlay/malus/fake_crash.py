"""Fake crash : faux écran bleu d'erreur (simple dessin sur l'overlay, aucun lien avec Vanguard)."""

from __future__ import annotations

from chaos_overlay.malus.base import EffectContext, Malus, register

BACKGROUND = "#003399"
MESSAGE = "VANGUARD ANTI-CHEAT CRITICAL ERROR\nDisconnecting..."


@register
class FakeCrash(Malus):
    key = "fake_crash"
    default_duration_ms = 2500

    def _draw(self, ctx: EffectContext) -> None:
        canvas = ctx.canvas
        self._track(canvas.create_rectangle(0, 0, ctx.width, ctx.height, fill=BACKGROUND, outline=""))
        self._track(
            canvas.create_text(
                ctx.width // 2,
                ctx.height // 2,
                text=MESSAGE,
                fill="white",
                font=("Courier", 28, "bold"),
                justify="center",
            )
        )
