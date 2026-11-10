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
from tkinter import messagebox

import customtkinter as ctk

from chaos_overlay import config, scheduler, theme
from chaos_overlay.hotkey import HomeHotkey
from chaos_overlay.logs import setup_logging
from chaos_overlay.malus import REGISTRY
from chaos_overlay.paths import app_dir
from chaos_overlay.ui.dashboard import Dashboard
from chaos_overlay.ui.overlay import OverlayWindow
from chaos_overlay.ui.roulette import RouletteView
from chaos_overlay.ui.splash import SplashScreen

logger = logging.getLogger(__name__)

DEFAULT_FREQUENCY_S = config.DEFAULT_FREQUENCY_S
CRASH_LOG_NAME = "crash_log.txt"

# HOME passe désormais par RegisterHotKey (hotkey.py) : plus besoin d'être administrateur.
HOTKEY_WARNING = (
    "La touche HOME est déjà utilisée par un autre programme :\n"
    "le Dashboard ne pourra pas être rouvert en jeu."
)
CLICK_THROUGH_WARNING = (
    "Impossible de rendre l'overlay transparent aux clics.\n"
    "Les malus affichés risquent de bloquer la souris : ferme l'application si c'est le cas."
)


class ChaosApp:
    """L'application : réglages, minuteur, tirage, roulette puis malus."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Chaos Overlay - Core")

        self.rng = random.Random()
        # Réglages de chaos_config.json (valeurs par défaut si le fichier est absent ou abîmé).
        self.config_path = config.config_path()
        self.config = config.load(self.config_path)
        self.timer_interval = tk.IntVar(value=self.config.frequency_s)
        # Une case par malus, dans l'ordre du registre, cochée selon la config.
        self.malus_states = {key: tk.BooleanVar(value=self.config.enabled[key]) for key in REGISTRY}
        self.timer_id: str | None = None

        self.dashboard = Dashboard(root, self.timer_interval, self.malus_states, on_start=self.start_clicked)
        # Ordre conservé : HOME (et son avertissement) avant l'overlay.
        self.hotkey = HomeHotkey(self.dashboard.open, root.after)
        if not self.hotkey.start():
            messagebox.showwarning("Attention", HOTKEY_WARNING)

        self.overlay = OverlayWindow(root)
        if not self.overlay.click_through:
            messagebox.showwarning("Attention", CLICK_THROUGH_WARNING)

        self.roulette = RouletteView(self.overlay.canvas, root.after, self.rng, self.overlay.height)
        self.splash = SplashScreen(root, on_done=self.dashboard.open)

    def start_clicked(self) -> None:
        """Bouton « Démarrer le chaos » : enregistre les réglages, puis (re)lance le minuteur."""
        self.save_config()
        self.start_timer()

    def save_config(self) -> bool:
        """Recopie la fréquence et les cases du Dashboard dans la config, puis l'écrit sur disque."""
        frequency = config.clamp_frequency(self.timer_interval.get())
        if frequency != self.timer_interval.get():
            logger.info("Fréquence ramenée à %d s (bornes %d à %d)", frequency, config.MIN_FREQUENCY_S, config.MAX_FREQUENCY_S)
            self.timer_interval.set(frequency)
        self.config.frequency_s = frequency
        self.config.enabled = {key: variable.get() for key, variable in self.malus_states.items()}
        return config.save(self.config, self.config_path)

    def close(self) -> None:
        """À la sortie : libère la touche HOME."""
        self.hotkey.stop()

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
        """Démarre une nouvelle instance du malus tiré ("rien" : aucun effet), puis relance le minuteur.

        Chaque malus reçoit la durée de la config (durations_ms).
        """
        try:
            malus_class = REGISTRY.get(key)
            if malus_class is not None:
                duration_ms = self.config.durations_ms.get(key)
                malus_class(duration_ms).start(self.overlay.make_context(self.rng))
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
    # Avant _silence_missing_std_streams : la console n'est branchée que si un vrai stderr existe.
    setup_logging()
    _silence_missing_std_streams()
    ctk.set_appearance_mode(theme.APPEARANCE_MODE)
    ctk.set_default_color_theme(theme.COLOR_THEME)
    try:
        root = tk.Tk()
        app = ChaosApp(root)
        try:
            root.mainloop()
        finally:
            app.close()
    except Exception:
        logger.exception("Erreur fatale, trace écrite dans %s", CRASH_LOG_NAME)
        _write_crash_log()
        os._exit(1)
