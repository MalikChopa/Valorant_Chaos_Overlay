"""MLG plein écran : joue mlg.gif au centre de l'écran pendant 6 s.

Les images du GIF sont chargées au premier déclenchement (pas au démarrage),
et seulement celles qu'on a le temps d'afficher : ceil(6000 / 40) = 150 images.
Elles restent ensuite en cache pour les déclenchements suivants.
"""

from __future__ import annotations

import logging
import math
import tkinter as tk
from pathlib import Path

from chaos_overlay.malus.base import EffectContext, Malus, register
from chaos_overlay.paths import resource_path

GIF_FILENAME = "mlg.gif"
FRAME_DELAY_MS = 40

logger = logging.getLogger(__name__)

# Cache des images déjà chargées : (chemin, nombre d'images) -> images.
_frame_cache: dict[tuple[str, int], list[tk.PhotoImage]] = {}


def frames_needed(duration_ms: int, frame_delay_ms: int = FRAME_DELAY_MS) -> int:
    """Nombre d'images affichées pendant l'effet (ceil(durée / délai))."""
    return math.ceil(duration_ms / frame_delay_ms)


def load_frames(gif_path: Path, max_frames: int, master: tk.Misc) -> list[tk.PhotoImage]:
    """Lit au plus `max_frames` images du GIF ; s'arrête à la dernière image du fichier."""
    frames: list[tk.PhotoImage] = []
    for index in range(max_frames):
        try:
            frames.append(tk.PhotoImage(master=master, file=str(gif_path), format=f"gif -index {index}"))
        except tk.TclError:
            break
    return frames


def get_frames(gif_path: Path, max_frames: int, master: tk.Misc) -> list[tk.PhotoImage]:
    """Images du GIF, depuis le cache si possible. Liste vide si le fichier est absent."""
    if not gif_path.exists():
        logger.warning("%s introuvable (%s) : le malus MLG ne fait rien.", GIF_FILENAME, gif_path)
        return []
    cache_key = (str(gif_path), max_frames)
    if cache_key not in _frame_cache:
        _frame_cache[cache_key] = load_frames(gif_path, max_frames, master)
    return _frame_cache[cache_key]


@register
class MlgGif(Malus):
    key = "mlg_fullscreen"
    default_duration_ms = 6000

    def __init__(self, duration_ms: int | None = None) -> None:
        super().__init__(duration_ms)
        self.frames: list[tk.PhotoImage] = []
        self.image_item = 0

    def _draw(self, ctx: EffectContext) -> None:
        gif_path = resource_path(GIF_FILENAME)
        self.frames = get_frames(gif_path, frames_needed(self.duration_ms), ctx.canvas)
        if not self.frames:
            return
        self.image_item = self._track(ctx.canvas.create_image(ctx.width // 2, ctx.height // 2, image=self.frames[0]))
        self._show_frame(ctx, 0)

    def _show_frame(self, ctx: EffectContext, frame_index: int) -> None:
        """Affiche une image puis programme la suivante (on boucle si le GIF est plus court)."""
        ctx.canvas.itemconfig(self.image_item, image=self.frames[frame_index])
        next_index = (frame_index + 1) % len(self.frames)
        self._schedule(FRAME_DELAY_MS, lambda: self._show_frame(ctx, next_index))
