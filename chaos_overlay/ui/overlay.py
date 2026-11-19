"""Fenêtre de l'overlay : plein écran, transparente, au premier plan, transparente aux clics.

Elle ne dessine que ses propres malus et la roulette. Elle ne capture pas l'écran et ne
regarde pas ce qu'il y a dessous. L'animation ne tourne que tant qu'il y a quelque chose
à afficher : au repos, l'overlay ne consomme rien.
"""

from __future__ import annotations

import random
import time
from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtCore import QRect, Qt, QTimer
from PySide6.QtGui import QGuiApplication, QPainter, QPaintEvent, QScreen
from PySide6.QtWidgets import QWidget

from chaos_overlay import win32
from chaos_overlay.malus.base import REFERENCE_HEIGHT, EffectContext, Malus
from chaos_overlay.profiles import GameProfile
from chaos_overlay.ui.roulette import Roulette, paint_roulette

# Une image toutes les 33 ms (≈ 30 i/s) : fluide, sans peser sur le jeu.
FRAME_INTERVAL_MS = 33

Clock = Callable[[], int]


def monotonic_ms() -> int:
    """Horloge monotone en millisecondes."""
    return time.monotonic_ns() // 1_000_000


@dataclass
class ActiveMalus:
    """Un malus en cours et l'instant (horloge de l'overlay) où il a commencé."""

    malus: Malus
    started_ms: int


class OverlayWindow(QWidget):
    """Fenêtre transparente qui couvre un écran et y dessine les malus actifs et la roulette."""

    def __init__(self, clock: Clock = monotonic_ms) -> None:
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool  # pas d'icône dans la barre des tâches
            | Qt.WindowType.WindowTransparentForInput  # clics et clavier passent au travers
            | Qt.WindowType.WindowDoesNotAcceptFocus,
        )
        self.setWindowTitle("Chaos Overlay")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.clock = clock
        self.effects: list[ActiveMalus] = []
        self.roulette: Roulette | None = None
        self.click_through = False

        self._frame_timer = QTimer(self)
        self._frame_timer.setInterval(FRAME_INTERVAL_MS)
        self._frame_timer.timeout.connect(self._on_frame)

    # --- Placement -------------------------------------------------------------------------

    def show_on(self, screen: QScreen) -> None:
        """Couvre tout l'écran `screen`, s'affiche, puis vérifie la transparence aux clics."""
        self.setGeometry(screen.geometry())
        self.show()
        self.click_through = self._apply_click_through()

    def _apply_click_through(self) -> bool:
        """Sous Windows, ajoute et vérifie les styles Win32 ; ailleurs (ou sans écran), le drapeau Qt suffit."""
        if QGuiApplication.platformName() != "windows":
            return True
        return win32.make_click_through(int(self.winId()))

    def context(self, rng: random.Random, profile: GameProfile) -> EffectContext:
        """Contexte donné à chaque malus : taille de l'overlay, hasard, profil de jeu."""
        width = self.width() or 1920
        height = self.height() or REFERENCE_HEIGHT
        return EffectContext(width=width, height=height, rng=rng, profile=profile)

    # --- Malus -----------------------------------------------------------------------------

    def add_effect(self, malus: Malus) -> None:
        """Démarre un malus maintenant (il se superpose à ceux déjà en cours)."""
        self.effects.append(ActiveMalus(malus, self.clock()))
        self.wake()

    def wake(self) -> None:
        """Relance l'animation (appelé quand un malus ou la roulette apparaît ou change)."""
        if not self._frame_timer.isActive():
            self._frame_timer.start()
        self.update()

    @property
    def is_animating(self) -> bool:
        return self._frame_timer.isActive()

    def prune(self) -> None:
        """Retire les malus terminés."""
        now = self.clock()
        self.effects = [item for item in self.effects if not item.malus.is_finished(now - item.started_ms)]

    def _on_frame(self) -> None:
        self.prune()
        if not self.effects and not (self.roulette is not None and self.roulette.visible):
            self._frame_timer.stop()
        self.update()

    # --- Dessin ----------------------------------------------------------------------------

    def paint_frame(self, painter: QPainter, now_ms: int) -> None:
        """Dessine l'image de l'instant `now_ms` : les malus dans l'ordre d'arrivée, puis la roulette."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for item in self.effects:
            item.malus.render(painter, now_ms - item.started_ms)
        if self.roulette is not None:
            height = self.height() or REFERENCE_HEIGHT
            paint_roulette(painter, self.roulette, height / REFERENCE_HEIGHT, height)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802 (nom imposé par Qt)
        painter = QPainter(self)
        try:
            # Fond entièrement transparent : on n'efface que nos propres pixels.
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(QRect(0, 0, self.width(), self.height()), Qt.GlobalColor.transparent)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            self.paint_frame(painter, self.clock())
        finally:
            painter.end()
