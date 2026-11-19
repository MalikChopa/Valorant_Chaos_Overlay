"""Contrat commun des malus : contexte, classe de base et registre.

Un malus est un objet qui sait se dessiner à un instant donné : `render(painter, elapsed_ms)`.
Il ne crée ni fenêtre ni minuteur. L'overlay l'appelle à chaque image et le retire quand
`is_finished(elapsed_ms)` devient vrai. Conséquences :
- plusieurs malus se superposent sans partager d'état ;
- un test peut dessiner n'importe quel instant dans une QImage, sans fenêtre ni attente.

Les tirages au hasard se font une fois, dans `setup()`, au déclenchement : le rendu d'un
instant donné est donc toujours le même.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar, TypeVar

from PySide6.QtGui import QPainter

from chaos_overlay.profiles import DEFAULT_PROFILE, GameProfile, get_profile

# Hauteur d'écran de référence : à 1080 px, les tailles des malus sont celles de la v2.
REFERENCE_HEIGHT = 1080


@dataclass(frozen=True)
class EffectContext:
    """Ce dont un malus a besoin : la taille de l'écran, le hasard et le profil de jeu."""

    width: int
    height: int
    rng: random.Random
    profile: GameProfile = field(default_factory=lambda: get_profile(DEFAULT_PROFILE))

    @property
    def scale(self) -> float:
        """Facteur d'échelle : 1.0 en 1080p, 1.33 en 1440p, 2.0 en 4K."""
        return self.height / REFERENCE_HEIGHT

    def px(self, value: float) -> int:
        """Convertit une taille pensée pour du 1080p en pixels de cet écran (au moins 1)."""
        return max(1, round(value * self.scale))


class Malus(ABC):
    """Un effet visuel. Une instance par déclenchement, qui garde ses propres tirages.

    Les sous-classes définissent `key`, `label`, `description`, `default_duration_ms` et
    `paint()`. Elles peuvent régler les fondus (`fade_in_ms`, `fade_out_ms`) et faire
    leurs tirages au hasard dans `setup()`.
    """

    key: ClassVar[str]
    label: ClassVar[str]
    description: ClassVar[str]
    default_duration_ms: ClassVar[int]
    fade_in_ms: ClassVar[int] = 150
    fade_out_ms: ClassVar[int] = 300

    def __init__(self, ctx: EffectContext, duration_ms: int | None = None) -> None:
        self.ctx = ctx
        self.duration_ms = self.default_duration_ms if duration_ms is None else duration_ms
        self.setup()

    def setup(self) -> None:
        """Tirages au hasard et préparation, faits une seule fois au déclenchement."""

    def is_finished(self, elapsed_ms: int) -> bool:
        """Vrai quand l'effet a atteint sa durée."""
        return elapsed_ms >= self.duration_ms

    def opacity(self, elapsed_ms: int) -> float:
        """Opacité de l'effet (0 à 1) : fondu d'entrée, plein, fondu de sortie."""
        if elapsed_ms < 0 or self.is_finished(elapsed_ms):
            return 0.0
        # Les fondus ne dépassent jamais la moitié de l'effet (utile pour les durées courtes).
        half = self.duration_ms / 2
        fade_in = min(self.fade_in_ms, half)
        fade_out = min(self.fade_out_ms, half)
        value = 1.0
        if fade_in > 0 and elapsed_ms < fade_in:
            value = elapsed_ms / fade_in
        remaining = self.duration_ms - elapsed_ms
        if fade_out > 0 and remaining < fade_out:
            value = min(value, remaining / fade_out)
        return max(0.0, min(1.0, value))

    def render(self, painter: QPainter, elapsed_ms: int) -> None:
        """Dessine l'effet à l'instant `elapsed_ms` (rien avant le début ni après la fin)."""
        alpha = self.opacity(elapsed_ms)
        if alpha <= 0.0:
            return
        painter.save()
        try:
            painter.setOpacity(painter.opacity() * alpha)
            self.paint(painter, elapsed_ms)
        finally:
            painter.restore()

    @abstractmethod
    def paint(self, painter: QPainter, elapsed_ms: int) -> None:
        """Dessine l'effet ; l'opacité du fondu est déjà appliquée au painter."""


# Registre des malus, dans l'ordre d'affichage du Dashboard (ordre des imports dans __init__).
REGISTRY: dict[str, type[Malus]] = {}

MalusClass = TypeVar("MalusClass", bound=type[Malus])


def register(malus_class: MalusClass) -> MalusClass:
    """Décorateur : ajoute la classe au REGISTRY sous sa clé `key`."""
    key = malus_class.key
    if key in REGISTRY:
        raise ValueError(f"Malus déjà enregistré : {key}")
    REGISTRY[key] = malus_class
    return malus_class
