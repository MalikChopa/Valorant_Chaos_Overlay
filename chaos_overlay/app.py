"""Point d'entrée : assemble l'overlay, le Dashboard, la roulette et le minuteur des malus.

Rien ne se passe à l'import : tout le démarrage est dans main().
"""

from __future__ import annotations

import logging
import os
import random
import sys
import tkinter as tk
import traceback
from collections.abc import Callable
from tkinter import messagebox

import customtkinter as ctk
import keyboard

from chaos_overlay import scheduler, theme
from chaos_overlay.malus import REGISTRY
from chaos_overlay.paths import app_dir
from chaos_overlay.ui.dashboard import Dashboard
from chaos_overlay.ui.overlay import OverlayWindow
from chaos_overlay.ui.roulette import RouletteView
from chaos_overlay.ui.splash import SplashScreen

logger = logging.getLogger(__name__)

DEFAULT_FREQUENCY_S = 60
CRASH_LOG_NAME = "crash_log.txt"

HOTKEY_WARNING = (
    "L'application n'a pas été lancée en Administrateur !\n"
    "Le logiciel va s'ouvrir, mais la touche 'HOME' ne marchera pas en jeu."
)
CLICK_THROUGH_WARNING = (
    "Impossible de rendre l'overlay transparent aux clics.\n"
    "Les malus affichés risquent de bloquer la souris : ferme l'application si c'est le cas."
)


def register_home_hotkey(root: tk.Tk, callback: Callable[[], None]) -> bool:
    """Touche HOME -> callback dans la boucle Tk (lib `keyboard`, remplacée au J2).

    Renvoie False et affiche l'avertissement d'origine si l'enregistrement échoue.
    """
    try:
        keyboard.add_hotkey("home", lambda: root.after(0, callback))
    except Exception:
        logger.warning("Raccourci HOME non enregistré", exc_info=True)
        messagebox.showwarning("Attention", HOTKEY_WARNING)
        return False
    return True


class ChaosApp:
    """L'application : réglages, minuteur, tirage, roulette puis malus."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Chaos Overlay - Core")

        self.rng = random.Random()
        self.timer_interval = tk.IntVar(value=DEFAULT_FREQUENCY_S)
        # Une case par malus, cochée par défaut, dans l'ordre du registre.
        self.malus_states = {key: tk.BooleanVar(value=True) for key in REGISTRY}
        self.timer_id: str | None = None

        self.dashboard = Dashboard(root, self.timer_interval, self.malus_states, on_start=self.start_timer)
        register_home_hotkey(root, self.dashboard.open)

        self.overlay = OverlayWindow(root)
        if not self.overlay.click_through:
            messagebox.showwarning("Attention", CLICK_THROUGH_WARNING)

        self.roulette = RouletteView(self.overlay.canvas, root.after, self.rng, self.overlay.height)
        self.splash = SplashScreen(root, on_done=self.dashboard.open)

    def start_timer(self) -> None:
        """(Re)lance le compte à rebours jusqu'au prochain malus."""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.timer_id = self.root.after(self.timer_interval.get() * 1000, self.trigger_malus)

    def active_malus(self) -> list[str]:
        """Clés des malus cochés dans le Dashboard."""
        return [key for key, variable in self.malus_states.items() if variable.get()]

    def trigger_malus(self) -> None:
        """Tire le malus puis lance la roulette."""
        active = self.active_malus()
        final_key = scheduler.pick(active, self.rng)
        self.roulette.spin(final_key, scheduler.roulette_pool(active), on_done=self.execute_malus)

    def execute_malus(self, key: str) -> None:
        """Démarre une nouvelle instance du malus tiré ("rien" : aucun effet), puis relance le minuteur."""
        try:
            malus_class = REGISTRY.get(key)
            if malus_class is not None:
                malus_class().start(self.overlay.make_context(self.rng))
        finally:
            # Même si un malus plante, le chaos continue.
            self.start_timer()


def _silence_missing_std_streams() -> None:
    """Version exe sans console : stdout/stderr valent None ; on les envoie vers os.devnull."""
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")


def _write_crash_log() -> None:
    """Écrit la trace de l'erreur dans crash_log.txt, à côté de l'exe (ou à la racine du projet)."""
    crash_path = app_dir() / CRASH_LOG_NAME
    with open(crash_path, "w", encoding="utf-8") as crash_file:
        crash_file.write(traceback.format_exc())


def main() -> None:
    """Lance l'application (bloquant jusqu'à la fermeture)."""
    _silence_missing_std_streams()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    ctk.set_appearance_mode(theme.APPEARANCE_MODE)
    ctk.set_default_color_theme(theme.COLOR_THEME)
    try:
        root = tk.Tk()
        ChaosApp(root)
        root.mainloop()
    except Exception:
        _write_crash_log()
        os._exit(1)
