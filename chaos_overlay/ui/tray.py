"""Icône dans la zone de notification de Windows : état du chaos et raccourcis.

Clic sur l'icône : ouvre le Dashboard. Menu (clic droit) : Dashboard, Pause/Reprendre,
Malus maintenant, Quitter. L'infobulle donne le temps avant le prochain malus.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from chaos_overlay.ui.icon import app_icon


class TrayIcon(QSystemTrayIcon):
    """Zone de notification. N'agit que par signaux : c'est l'appli qui décide."""

    open_requested = Signal()
    pause_toggled = Signal()
    trigger_requested = Signal()
    quit_requested = Signal()

    def __init__(self) -> None:
        super().__init__(app_icon())
        self._icons = {False: app_icon(paused=False), True: app_icon(paused=True)}
        self.menu = QMenu()
        self.open_action = self.menu.addAction("Ouvrir le Dashboard")
        self.open_action.triggered.connect(self.open_requested.emit)
        self.menu.addSeparator()
        self.pause_action = self.menu.addAction("Mettre en pause")
        self.pause_action.triggered.connect(self.pause_toggled.emit)
        self.trigger_action = self.menu.addAction("Lancer un malus maintenant")
        self.trigger_action.triggered.connect(self.trigger_requested.emit)
        self.menu.addSeparator()
        self.quit_action = self.menu.addAction("Quitter")
        self.quit_action.triggered.connect(self.quit_requested.emit)
        self.setContextMenu(self.menu)
        self.activated.connect(self._on_activated)
        self.set_state(running=False, paused=False, status="Chaos à l'arrêt")

    def set_state(self, running: bool, paused: bool, status: str) -> None:
        """Met à jour l'icône, l'infobulle et le menu selon l'état du chaos."""
        self.setIcon(self._icons[paused])
        self.setToolTip(f"Chaos Overlay\n{status}")
        self.pause_action.setText("Reprendre le chaos" if paused else "Mettre en pause")
        self.pause_action.setEnabled(running or paused)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.open_requested.emit()
