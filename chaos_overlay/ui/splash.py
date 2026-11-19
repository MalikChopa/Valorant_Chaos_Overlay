"""Écran de démarrage (environ 1,2 s), puis ouverture du Dashboard."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget

from chaos_overlay import __version__

WIDTH = 500
HEIGHT = 300
STEP_MS = 60
STEP_VALUE = 5  # en %, donc 20 pas de 60 ms


class SplashScreen(QWidget):
    """Fenêtre sans bordure avec titre et barre de progression ; appelle on_done à la fin."""

    def __init__(self, on_done: Callable[[], None]) -> None:
        super().__init__(
            None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SplashScreen
        )
        self.setObjectName("splash")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setFixedSize(WIDTH, HEIGHT)
        self.on_done = on_done

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 40, 50, 40)
        title = QLabel("CHAOS OVERLAY")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle = QLabel(f"by Chopa · v{__version__}")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 100)
        layout.addStretch(1)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(30)
        layout.addWidget(self.progress)
        layout.addStretch(1)

        self._timer = QTimer(self)
        self._timer.setInterval(STEP_MS)
        self._timer.timeout.connect(self._step)

    def start(self) -> None:
        """Affiche l'écran au centre de l'écran principal et lance la barre."""
        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            self.move(screen.availableGeometry().center() - self.rect().center())
        self.show()
        self._timer.start()

    def _step(self) -> None:
        """Avance la barre de 5 % ; à 100 %, ferme et appelle on_done."""
        value = self.progress.value() + STEP_VALUE
        if value < 100:
            self.progress.setValue(value)
            return
        self._timer.stop()
        self.close()
        self.on_done()
