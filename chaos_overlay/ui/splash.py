"""Écran de chargement affiché au démarrage (environ 1,2 s), puis ouverture du Dashboard."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

import customtkinter as ctk

from chaos_overlay import theme

WIDTH = 500
HEIGHT = 300
STEP_MS = 60
STEP_VALUE = 0.05


class SplashScreen:
    """Fenêtre sans bordure avec titre et barre de progression ; appelle on_done à la fin."""

    def __init__(self, root: tk.Tk, on_done: Callable[[], None]) -> None:
        self.root = root
        self.on_done = on_done

        self.window = ctk.CTkToplevel(root)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(fg_color=theme.BACKGROUND)

        x = (root.winfo_screenwidth() - WIDTH) // 2
        y = (root.winfo_screenheight() - HEIGHT) // 2
        self.window.geometry(f"{WIDTH}x{HEIGHT}+{int(x)}+{int(y)}")

        font = theme.FONT_FAMILY
        ctk.CTkLabel(self.window, text="VALORANT", font=(font, 40, "bold"), text_color=theme.TEXT).pack(
            pady=(40, 0)
        )
        ctk.CTkLabel(self.window, text="CHAOS OVERLAY", font=(font, 30, "bold"), text_color=theme.ACCENT).pack(
            pady=(0, 20)
        )
        ctk.CTkLabel(self.window, text="Made by Chupa", font=(font, 14, "italic"), text_color=theme.MUTED).pack()

        self.progressbar = ctk.CTkProgressBar(
            self.window, width=400, height=10, progress_color=theme.ACCENT, fg_color=theme.PANEL
        )
        self.progressbar.pack(pady=40)
        self.progressbar.set(0)

        self.window.update_idletasks()  # Force l'affichage immédiat
        self._update_progress(0)

    def _update_progress(self, value: float) -> None:
        """Avance la barre de 5 % toutes les 60 ms ; à 100 %, ferme et appelle on_done."""
        if value < 1.0:
            self.progressbar.set(value)
            self.root.after(STEP_MS, lambda: self._update_progress(value + STEP_VALUE))
        else:
            self.window.destroy()
            self.on_done()
