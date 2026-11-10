"""Fenêtre de l'overlay : plein écran, transparente, au premier plan, transparente aux clics."""

from __future__ import annotations

import random
import tkinter as tk

from chaos_overlay import theme, win32
from chaos_overlay.malus.base import EffectContext


class OverlayWindow:
    """Transforme la fenêtre racine Tk en overlay et porte le Canvas où les malus dessinent."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.width = root.winfo_screenwidth()
        self.height = root.winfo_screenheight()
        root.geometry(f"{self.width}x{self.height}+0+0")
        root.overrideredirect(True)
        root.wm_attributes("-topmost", True)

        root.config(bg=theme.TRANSPARENT)
        root.wm_attributes("-transparentcolor", theme.TRANSPARENT)

        # False si Windows a refusé : app.py affiche alors un avertissement.
        self.click_through = self._make_click_through()

        self.canvas = tk.Canvas(
            root, width=self.width, height=self.height, bg=theme.TRANSPARENT, highlightthickness=0
        )
        self.canvas.pack()

    def _make_click_through(self) -> bool:
        """Applique les styles Win32 qui laissent passer les clics à travers l'overlay."""
        self.root.update_idletasks()
        hwnd = win32.toplevel_hwnd(self.root.winfo_id())
        return win32.make_click_through(hwnd)

    def make_context(self, rng: random.Random) -> EffectContext:
        """Contexte donné à chaque malus : canvas, taille de l'écran, minuteur Tk, hasard."""
        return EffectContext(
            canvas=self.canvas,
            width=self.width,
            height=self.height,
            after=self.root.after,
            after_cancel=self.root.after_cancel,
            rng=rng,
        )
