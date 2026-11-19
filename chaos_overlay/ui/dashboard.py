"""Dashboard : profil de jeu, écran, fréquence, malus (case, durée, test), « Démarrer » et « Quitter ».

Le Dashboard ne connaît que la config : `load(config)` remplit les champs, `to_config()`
les relit. Il signale les clics par `start_requested` et `quit_requested` ; c'est l'appli
qui enregistre et lance le chaos. `preview_requested(clé)` demande d'afficher un malus tout
de suite, pour le tester sans attendre la roulette.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCloseEvent, QGuiApplication
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from chaos_overlay import config as config_module
from chaos_overlay.config import Config
from chaos_overlay.malus.base import Malus
from chaos_overlay.profiles import GameProfile

WIDTH = 520
HEIGHT = 820


class MalusRow(QWidget):
    """Une ligne de la liste : case à cocher (description en infobulle), durée en secondes, bouton « Tester »."""

    def __init__(self, malus_class: type[Malus], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.key = malus_class.key
        self.checkbox = QCheckBox(malus_class.label.upper())
        self.checkbox.setToolTip(malus_class.description)
        self.duration = QDoubleSpinBox()
        self.duration.setRange(config_module.MIN_DURATION_MS / 1000, config_module.MAX_DURATION_MS / 1000)
        self.duration.setSingleStep(0.5)
        self.duration.setDecimals(1)
        self.duration.setSuffix(" s")
        self.duration.setToolTip("Durée du malus")
        self.duration.setFixedWidth(90)
        self.test_button = QPushButton("▶")
        self.test_button.setObjectName("small")
        self.test_button.setToolTip("Tester ce malus maintenant")
        self.test_button.setFixedWidth(36)
        self.test_button.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.addWidget(self.checkbox, 1)
        layout.addWidget(self.duration)
        layout.addWidget(self.test_button)


class Dashboard(QWidget):
    """Panneau de réglages. Une seule fenêtre : open() la (ré)affiche au premier plan."""

    start_requested = Signal()
    quit_requested = Signal()
    preview_requested = Signal(str)

    def __init__(
        self,
        cfg: Config,
        malus_classes: Mapping[str, type[Malus]],
        profiles: Mapping[str, GameProfile],
        screen_names: Sequence[str],
    ) -> None:
        super().__init__(None, Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.setObjectName("dashboard")
        self.setWindowTitle("Chaos Overlay - Dashboard")
        self.resize(WIDTH, HEIGHT)
        self._base = cfg

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 14)
        root.setSpacing(10)

        title = QLabel("CHAOS OVERLAY")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle = QLabel("by Chopa")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)
        root.addWidget(subtitle)

        # Réglages généraux.
        panel = QFrame()
        panel.setObjectName("panel")
        form = QFormLayout(panel)
        form.setContentsMargins(15, 12, 15, 12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.profile_box = QComboBox()
        for profile in profiles.values():
            self.profile_box.addItem(profile.name, profile.key)
        self.profile_box.setToolTip("Règle les zones masquées par « HUD masqué ». Aucune détection du jeu.")
        form.addRow("Profil de jeu", self.profile_box)

        self.screen_box = QComboBox()
        for index, name in enumerate(screen_names):
            self.screen_box.addItem(name, index)
        form.addRow("Écran", self.screen_box)

        self.frequency = QSpinBox()
        self.frequency.setRange(config_module.MIN_FREQUENCY_S, config_module.MAX_FREQUENCY_S)
        self.frequency.setSuffix(" s")
        self.frequency.setToolTip("Temps entre deux malus")
        form.addRow("Fréquence", self.frequency)
        root.addWidget(panel)

        # Liste des malus.
        header = QHBoxLayout()
        section = QLabel("ACTIVATION DES MALUS")
        section.setObjectName("section")
        header.addWidget(section, 1)
        for text, checked in (("Tout", True), ("Aucun", False)):
            button = QPushButton(text)
            button.setObjectName("small")
            button.clicked.connect(lambda _=False, value=checked: self.set_all(value))
            header.addWidget(button)
        root.addLayout(header)

        rows_widget = QWidget()
        rows_widget.setObjectName("malusRows")
        rows_layout = QVBoxLayout(rows_widget)
        rows_layout.setContentsMargins(0, 6, 0, 6)
        rows_layout.setSpacing(0)
        self.rows: dict[str, MalusRow] = {}
        for key, malus_class in malus_classes.items():
            row = MalusRow(malus_class)
            row.test_button.clicked.connect(lambda _=False, malus_key=key: self.preview_requested.emit(malus_key))
            self.rows[key] = row
            rows_layout.addWidget(row)
        rows_layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setObjectName("malusList")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(rows_widget)
        root.addWidget(scroll, 1)

        # Boutons.
        self.start_button = QPushButton("▶  DÉMARRER LE CHAOS")
        self.start_button.setObjectName("primary")
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_button.clicked.connect(self._start_clicked)
        root.addWidget(self.start_button)

        self.quit_button = QPushButton("✕  QUITTER")
        self.quit_button.clicked.connect(self.quit_requested.emit)
        root.addWidget(self.quit_button)

        self.status = QLabel("Chaos à l'arrêt")
        self.status.setObjectName("status")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.status)

        hint = QLabel("HOME ou l'icône de la zone de notification rouvrent ce menu, même en jeu")
        hint.setObjectName("hint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setWordWrap(True)
        root.addWidget(hint)

        self.load(cfg)

    # --- Config <-> champs -----------------------------------------------------------------

    def load(self, cfg: Config) -> None:
        """Remplit les champs avec la config."""
        self._base = cfg
        self._select(self.profile_box, cfg.profile)
        self._select(self.screen_box, cfg.screen)
        self.frequency.setValue(cfg.frequency_s)
        for key, row in self.rows.items():
            row.checkbox.setChecked(cfg.enabled.get(key, True))
            row.duration.setValue(cfg.durations_ms.get(key, config_module.MIN_DURATION_MS) / 1000)

    def to_config(self) -> Config:
        """Config lue dans les champs (les valeurs sont déjà dans les bornes grâce aux widgets)."""
        return Config(
            frequency_s=self.frequency.value(),
            enabled={key: row.checkbox.isChecked() for key, row in self.rows.items()},
            durations_ms={
                key: config_module.clamp_duration(round(row.duration.value() * 1000)) for key, row in self.rows.items()
            },
            profile=str(self.profile_box.currentData() or self._base.profile),
            screen=int(self.screen_box.currentData() or 0),
            hotkey=self._base.hotkey,
        )

    def set_status(self, text: str) -> None:
        """Ligne d'état sous les boutons (« Prochain malus dans 42 s », « En pause »...)."""
        self.status.setText(text)

    def set_all(self, checked: bool) -> None:
        """Coche ou décoche tous les malus."""
        for row in self.rows.values():
            row.checkbox.setChecked(checked)

    @staticmethod
    def _select(box: QComboBox, value: object) -> None:
        index = box.findData(value)
        box.setCurrentIndex(index if index >= 0 else 0)

    # --- Fenêtre ---------------------------------------------------------------------------

    def open(self) -> None:
        """Affiche le Dashboard au centre de l'écran principal, au premier plan."""
        if not self.isVisible():
            screen = QGuiApplication.primaryScreen()
            if screen is not None:
                area = screen.availableGeometry()
                self.move(area.center() - self.rect().center())
        self.show()
        self.raise_()
        self.activateWindow()

    def _start_clicked(self) -> None:
        """Ferme le panneau et demande le (re)démarrage du chaos."""
        self.hide()
        self.start_requested.emit()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 (nom imposé par Qt)
        """La croix cache le panneau ; HOME le rouvre. Seul « Quitter » ferme l'appli."""
        event.ignore()
        self.hide()
