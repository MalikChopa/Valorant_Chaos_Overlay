"""Dashboard CustomTkinter : fréquence, cases des malus, boutons « Démarrer le chaos » et « Quitter »."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from typing import Any

import customtkinter as ctk

from chaos_overlay import scheduler, theme

WIDTH = 450
HEIGHT = 750


class Dashboard:
    """Panneau de réglages. Une seule fenêtre à la fois : open() la remet au premier plan si elle existe."""

    def __init__(
        self,
        root: tk.Tk,
        timer_interval: tk.IntVar,
        malus_states: dict[str, tk.BooleanVar],
        on_start: Callable[[], None],
        on_quit: Callable[[], None],
    ) -> None:
        self.root = root
        self.timer_interval = timer_interval
        self.malus_states = malus_states
        self.on_start = on_start
        self.on_quit = on_quit
        self.window: Any = None  # ctk.CTkToplevel quand le panneau est ouvert

    def open(self) -> None:
        """Ouvre le Dashboard (ou le remet au premier plan s'il est déjà ouvert)."""
        if self.window is not None and self.window.winfo_exists():
            self.window.focus()
            return

        font = theme.FONT_FAMILY
        window = ctk.CTkToplevel(self.root)
        self.window = window
        window.title("Dashboard - Made by Chupa")

        x = (self.root.winfo_screenwidth() - WIDTH) // 2
        y = (self.root.winfo_screenheight() - HEIGHT) // 2
        window.geometry(f"{WIDTH}x{HEIGHT}+{int(x)}+{int(y)}")
        window.attributes("-topmost", True)
        window.configure(fg_color=theme.BACKGROUND)

        header = ctk.CTkFrame(window, fg_color=theme.BACKGROUND)
        header.pack(fill="x", pady=(20, 5))
        ctk.CTkLabel(header, text="DASHBOARD", font=(font, 32, "bold"), text_color=theme.TEXT).pack()
        ctk.CTkLabel(header, text="By Chupa", font=(font, 16, "italic"), text_color=theme.ACCENT).pack()

        config_frame = ctk.CTkFrame(window, fg_color=theme.PANEL, corner_radius=8)
        config_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(config_frame, text="Fréquence (secondes) :", font=(font, 15)).pack(side="left", padx=15, pady=15)

        timer_entry = ctk.CTkEntry(config_frame, width=70, font=(font, 16, "bold"), border_color=theme.ACCENT)
        timer_entry.insert(0, str(self.timer_interval.get()))
        timer_entry.pack(side="right", padx=15, pady=15)

        def update_timer(event: object) -> None:
            seconds = scheduler.parse_frequency(timer_entry.get())
            if seconds is not None:
                self.timer_interval.set(seconds)

        timer_entry.bind("<KeyRelease>", update_timer)

        ctk.CTkLabel(window, text="ACTIVATION DES MALUS", font=(font, 12, "bold"), text_color=theme.MUTED).pack(
            anchor="w", padx=20, pady=(15, 0)
        )

        scroll = ctk.CTkScrollableFrame(window, fg_color=theme.PANEL, corner_radius=8)
        scroll.pack(fill="both", expand=True, padx=20, pady=5)

        for malus_key, variable in self.malus_states.items():
            ctk.CTkCheckBox(
                scroll,
                text=scheduler.display_name(malus_key),
                variable=variable,
                font=(font, 13, "bold"),
                text_color=theme.TEXT,
                fg_color=theme.ACCENT,
                hover_color=theme.ACCENT_HOVER,
                border_color=theme.DIM,
            ).pack(anchor="w", pady=10, padx=10)

        ctk.CTkButton(
            window,
            text="▶ DÉMARRER LE CHAOS",
            font=(font, 18, "bold"),
            text_color=theme.TEXT,
            fg_color=theme.ACCENT,
            hover_color=theme.ACCENT_HOVER,
            corner_radius=6,
            height=55,
            command=self._start_clicked,
        ).pack(fill="x", padx=20, pady=(20, 8))

        ctk.CTkButton(
            window,
            text="✕ QUITTER",
            font=(font, 14, "bold"),
            text_color=theme.MUTED,
            fg_color=theme.PANEL,
            hover_color=theme.DIM,
            corner_radius=6,
            height=36,
            command=self.on_quit,
        ).pack(fill="x", padx=20, pady=(0, 12))

        ctk.CTkLabel(
            window, text="(Appuie sur HOME en jeu pour rouvrir ce menu)", font=(font, 11), text_color=theme.DIM
        ).pack(pady=(0, 10))

    def _start_clicked(self) -> None:
        """Ferme le panneau et (re)lance le minuteur des malus."""
        if self.window is not None:
            self.window.destroy()
        self.on_start()
