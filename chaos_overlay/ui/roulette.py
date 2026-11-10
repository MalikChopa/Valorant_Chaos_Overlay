"""Roulette affichée sur l'overlay avant chaque malus (rythme donné par scheduler.roulette_delays)."""

from __future__ import annotations

import random
import tkinter as tk
from collections.abc import Callable, Sequence

from chaos_overlay import scheduler, theme

BOX_X = 20
BOX_WIDTH = 350
BOX_HEIGHT = 80


class RouletteView:
    """Fait défiler des noms de malus de plus en plus lentement, puis affiche le résultat."""

    def __init__(
        self,
        canvas: tk.Canvas,
        after: Callable[[int, Callable[[], None]], str],
        rng: random.Random,
        screen_height: int,
    ) -> None:
        self.canvas = canvas
        self.after = after
        self.rng = rng
        self.screen_height = screen_height

    def spin(self, final_key: str, pool: Sequence[str], on_done: Callable[[str], None]) -> None:
        """Lance la roulette ; à la fin, efface la boîte et appelle on_done(final_key)."""
        y = self.screen_height // 3
        box = self.canvas.create_rectangle(
            BOX_X, y, BOX_X + BOX_WIDTH, y + BOX_HEIGHT, fill=theme.BACKGROUND, outline=theme.ACCENT, width=3
        )
        text = self.canvas.create_text(
            BOX_X + (BOX_WIDTH // 2),
            y + (BOX_HEIGHT // 2),
            text="...",
            fill=theme.TEXT,
            font=(theme.FONT_FAMILY, 22, "bold"),
            justify="center",
        )
        items = [box, text]
        delays = scheduler.roulette_delays()

        def finish() -> None:
            for item in items:
                self.canvas.delete(item)
            on_done(final_key)

        def show_spin(spin_index: int) -> None:
            if spin_index < len(delays):
                name = self.rng.choice(list(pool))
                self.canvas.itemconfig(text, text=scheduler.display_name(name))
                self.after(delays[spin_index], lambda: show_spin(spin_index + 1))
            else:
                self.canvas.itemconfig(text, text=f">> {scheduler.display_name(final_key)} <<", fill=theme.ACCENT)
                self.after(scheduler.ROULETTE_RESULT_PAUSE_MS, finish)

        show_spin(0)
