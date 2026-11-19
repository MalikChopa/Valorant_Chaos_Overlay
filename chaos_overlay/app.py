"""Point d'entrée : assemble l'overlay, le Dashboard, la roulette et le minuteur des malus.

Rien ne se passe à l'import : tout le démarrage est dans main().
"""

from __future__ import annotations

import logging
import math
import os
import random
import sys
import traceback
from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QGuiApplication, QScreen
from PySide6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from chaos_overlay import __version__, config, scheduler, theme
from chaos_overlay.hotkey import HomeHotkey
from chaos_overlay.logs import setup_logging
from chaos_overlay.malus import REGISTRY, label_of
from chaos_overlay.paths import app_dir
from chaos_overlay.profiles import PROFILES, get_profile
from chaos_overlay.ui.dashboard import Dashboard
from chaos_overlay.ui.icon import app_icon
from chaos_overlay.ui.overlay import Clock, OverlayWindow, monotonic_ms
from chaos_overlay.ui.roulette import Roulette, Scheduler
from chaos_overlay.ui.splash import SplashScreen
from chaos_overlay.ui.tray import TrayIcon

logger = logging.getLogger(__name__)

APP_NAME = "Chaos Overlay"
CRASH_LOG_NAME = "crash_log.txt"
STATUS_INTERVAL_MS = 500

HOTKEY_WARNING = (
    "La touche HOME est déjà utilisée par un autre programme :\n"
    "le Dashboard ne pourra pas être rouvert en jeu."
)
CLICK_THROUGH_WARNING = (
    "Impossible de rendre l'overlay transparent aux clics.\n"
    "Les malus affichés risquent de bloquer la souris : ferme l'application si c'est le cas."
)


def qt_after(delay_ms: int, callback: Callable[[], None]) -> None:
    """Programme `callback` dans la boucle Qt (équivalent de root.after en Tkinter)."""
    QTimer.singleShot(delay_ms, callback)


def screen_label(index: int, screen: QScreen) -> str:
    """Nom d'un écran dans le Dashboard : « Écran 1 : 1920 × 1080 »."""
    size = screen.geometry().size()
    return f"Écran {index + 1} : {size.width()} × {size.height()}"


class ChaosApp:
    """L'application : réglages, minuteur, tirage, roulette puis malus.

    États : à l'arrêt (avant le premier « Démarrer »), en marche, en pause.
    Le constructeur crée les fenêtres sans les afficher ; launch() les affiche.
    `after`, `clock` et `hotkey` servent aux tests (faux minuteur, fausse horloge, faux raccourci).
    """

    def __init__(
        self,
        config_path: Path | None = None,
        after: Scheduler = qt_after,
        clock: Clock = monotonic_ms,
        hotkey: HomeHotkey | None = None,
    ) -> None:
        self.rng = random.Random()
        # Réglages de chaos_config.json (valeurs par défaut si le fichier est absent ou abîmé).
        self.config_path = config_path if config_path is not None else config.config_path()
        self.config = config.load(self.config_path)
        self.running = False
        self.paused = False
        self._paused_remaining_ms: int | None = None
        self._start_notified = False

        self.overlay = OverlayWindow(clock)
        self.roulette = Roulette(after, self.rng, label_of, on_change=self.overlay.wake)
        self.overlay.roulette = self.roulette

        screens = QGuiApplication.screens()
        self.dashboard = Dashboard(
            self.config, REGISTRY, PROFILES, [screen_label(index, screen) for index, screen in enumerate(screens)]
        )
        self.dashboard.start_requested.connect(self.start_clicked)
        self.dashboard.quit_requested.connect(self.quit_clicked)
        self.dashboard.preview_requested.connect(self.preview)

        self.tray = TrayIcon()
        self.tray.open_requested.connect(self.dashboard.open)
        self.tray.pause_toggled.connect(self.toggle_pause)
        self.tray.trigger_requested.connect(self.trigger_now)
        self.tray.quit_requested.connect(self.quit_clicked)

        # Minuteur du prochain malus (un seul coup, relancé après chaque malus).
        self.chaos_timer = QTimer()
        self.chaos_timer.setSingleShot(True)
        self.chaos_timer.timeout.connect(self.trigger_malus)

        # Rafraîchit le compte à rebours affiché (Dashboard et infobulle de l'icône).
        self.status_timer = QTimer()
        self.status_timer.setInterval(STATUS_INTERVAL_MS)
        self.status_timer.timeout.connect(self.refresh_status)

        self.hotkey = hotkey if hotkey is not None else HomeHotkey(self.dashboard.open, after)
        self.splash: SplashScreen | None = None
        self.refresh_status()

    # --- Démarrage et arrêt ----------------------------------------------------------------

    def launch(self) -> None:
        """Enregistre HOME, affiche l'overlay et l'icône, puis l'écran de démarrage et le Dashboard."""
        if not self.hotkey.start():
            QMessageBox.warning(None, "Attention", HOTKEY_WARNING)
        self.overlay.show_on(self.screen_for(self.config.screen))
        if not self.overlay.click_through:
            QMessageBox.warning(None, "Attention", CLICK_THROUGH_WARNING)
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray.show()
        self.status_timer.start()
        self.splash = SplashScreen(on_done=self.dashboard.open)
        self.splash.start()

    def close(self) -> None:
        """À la sortie : arrête les minuteurs, retire l'icône et libère la touche HOME."""
        self.chaos_timer.stop()
        self.status_timer.stop()
        self.tray.hide()
        self.hotkey.stop()

    @staticmethod
    def screen_for(index: int) -> QScreen:
        """Écran d'indice `index`, ou l'écran principal s'il n'existe plus (écran débranché)."""
        screens = QGuiApplication.screens()
        if 0 <= index < len(screens):
            return screens[index]
        primary = QGuiApplication.primaryScreen()
        assert primary is not None, "aucun écran détecté"
        return primary

    def _place_overlay(self, screen_index: int) -> None:
        """Affiche l'overlay sur l'écran choisi (s'il n'y est pas déjà)."""
        target = self.screen_for(screen_index)
        if self.overlay.geometry() != target.geometry() or not self.overlay.isVisible():
            self.overlay.show_on(target)

    # --- Commandes (Dashboard, icône de notification) --------------------------------------

    def start_clicked(self) -> None:
        """« Démarrer le chaos » : enregistre les réglages, place l'overlay, (re)lance le minuteur."""
        self.config = self.dashboard.to_config()
        config.save(self.config, self.config_path)
        self._place_overlay(self.config.screen)
        self.running, self.paused, self._paused_remaining_ms = True, False, None
        self.start_timer()
        self.refresh_status()
        if not self._start_notified and self.tray.isVisible():
            self._start_notified = True
            self.tray.showMessage(
                "Chaos lancé",
                f"Premier malus dans {self.config.frequency_s} s. HOME ou cette icône rouvrent le Dashboard.",
                QSystemTrayIcon.MessageIcon.Information,
                4000,
            )

    def toggle_pause(self) -> None:
        """Met le chaos en pause (le compte à rebours est gardé) ou le reprend."""
        if not self.running:
            return
        if self.paused:
            self.paused = False
            self.start_timer(self._paused_remaining_ms)
            self._paused_remaining_ms = None
        else:
            self.paused = True
            self._paused_remaining_ms = self.chaos_timer.remainingTime() if self.chaos_timer.isActive() else None
            self.chaos_timer.stop()
        self.refresh_status()

    def trigger_now(self) -> None:
        """Lance la roulette tout de suite (sauf si elle tourne déjà)."""
        if self.roulette.visible:
            return
        self.chaos_timer.stop()
        self._place_overlay(self.config.screen)
        self.trigger_malus()

    def preview(self, key: str) -> None:
        """Bouton « Tester » : affiche le malus tout de suite, avec les réglages du Dashboard, sans roulette."""
        settings = self.dashboard.to_config()
        self._place_overlay(settings.screen)
        self._start_malus(key, settings)

    def quit_clicked(self) -> None:
        """« Quitter » : arrête le minuteur et sort de la boucle Qt (main() appelle ensuite close())."""
        self.chaos_timer.stop()
        self.running = False
        app = QApplication.instance()
        if app is not None:
            app.quit()

    # --- Cycle des malus -------------------------------------------------------------------

    def start_timer(self, delay_ms: int | None = None) -> None:
        """(Re)lance le compte à rebours jusqu'au prochain malus (rien à l'arrêt ou en pause)."""
        if not self.running or self.paused:
            return
        self.chaos_timer.start(delay_ms if delay_ms is not None else self.config.frequency_s * 1000)

    def active_malus(self) -> list[str]:
        """Clés des malus cochés."""
        return [key for key in REGISTRY if self.config.enabled.get(key, False)]

    def trigger_malus(self) -> None:
        """Tire le malus puis lance la roulette."""
        active = self.active_malus()
        final_key = scheduler.pick(active, self.rng)
        self.roulette.spin(final_key, scheduler.roulette_pool(active), on_done=self.execute_malus)

    def execute_malus(self, key: str) -> None:
        """Démarre une nouvelle instance du malus tiré ("rien" : aucun effet), puis relance le minuteur."""
        try:
            self._start_malus(key, self.config)
        finally:
            self.start_timer()

    def _start_malus(self, key: str, settings: config.Config) -> None:
        """Ajoute le malus `key` à l'overlay. Un malus qui plante est journalisé, jamais fatal."""
        malus_class = REGISTRY.get(key)
        if malus_class is None:
            return
        try:
            ctx = self.overlay.context(self.rng, get_profile(settings.profile))
            self.overlay.add_effect(malus_class(ctx, settings.durations_ms.get(key)))
        except Exception:
            logger.exception("Le malus %s a planté", key)

    # --- État affiché ----------------------------------------------------------------------

    def status_text(self) -> str:
        """État du chaos en une phrase, pour le Dashboard et l'infobulle de l'icône."""
        if not self.running:
            return "Chaos à l'arrêt"
        if self.paused:
            return "Chaos en pause"
        if self.roulette.visible:
            return "Roulette en cours..."
        if self.chaos_timer.isActive():
            seconds = math.ceil(self.chaos_timer.remainingTime() / 1000)
            return f"Prochain malus dans {seconds} s"
        return "Malus en cours"

    def refresh_status(self) -> None:
        text = self.status_text()
        self.dashboard.set_status(text)
        self.tray.set_state(running=self.running, paused=self.paused, status=text)


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


def _create_qt_app() -> QApplication:
    """QApplication avec le nom, la police et la feuille de style de l'appli."""
    existing = QApplication.instance()
    qt_app = existing if isinstance(existing, QApplication) else QApplication(sys.argv)
    qt_app.setApplicationName(APP_NAME)
    qt_app.setApplicationVersion(__version__)
    # Fermer le Dashboard ne doit pas quitter : l'overlay reste et HOME rouvre le panneau.
    qt_app.setQuitOnLastWindowClosed(False)
    qt_app.setWindowIcon(app_icon())
    # Style Fusion + thème sombre : rendu identique partout, barre de titre sombre sous Windows 10/11.
    qt_app.setStyle("Fusion")
    qt_app.styleHints().setColorScheme(Qt.ColorScheme.Dark)
    font = QFont()
    font.setFamilies(theme.FONT_FALLBACKS)
    qt_app.setFont(font)
    qt_app.setStyleSheet(theme.STYLESHEET)
    return qt_app


def main() -> None:
    """Lance l'application (bloquant jusqu'à la fermeture)."""
    # Avant _silence_missing_std_streams : la console n'est branchée que si un vrai stderr existe.
    setup_logging()
    _silence_missing_std_streams()
    try:
        qt_app = _create_qt_app()
        app = ChaosApp()
        try:
            app.launch()
            qt_app.exec()
        finally:
            app.close()
    except Exception:
        logger.exception("Erreur fatale, trace écrite dans %s", CRASH_LOG_NAME)
        _write_crash_log()
        os._exit(1)
