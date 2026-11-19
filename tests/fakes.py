"""Faux minuteur et aide au rendu pour tester sans fenêtre ni attente."""

from __future__ import annotations

import random
from collections.abc import Callable

from PySide6.QtGui import QColor, QImage, QPainter

from chaos_overlay.malus.base import EffectContext, Malus
from chaos_overlay.profiles import DEFAULT_PROFILE, get_profile


class FakeClock:
    """Faux `after` / `after_cancel` : un temps virtuel en ms qu'on fait avancer à la main.

    À échéance égale, les rappels tournent dans l'ordre où ils ont été programmés (comme Qt et Tk).
    """

    def __init__(self) -> None:
        self.now = 0
        self._seq = 0
        self.pending: dict[str, tuple[int, int, Callable[[], object]]] = {}
        self.cancelled: list[str] = []

    def after(self, delay_ms: int, callback: Callable[[], object]) -> str:
        self._seq += 1
        after_id = f"after#{self._seq}"
        self.pending[after_id] = (self.now + delay_ms, self._seq, callback)
        return after_id

    def after_cancel(self, after_id: str) -> None:
        self.cancelled.append(after_id)
        self.pending.pop(after_id, None)

    def run_until(self, end_ms: int) -> None:
        """Exécute, dans l'ordre, tous les rappels dont l'échéance est <= end_ms."""
        while self.pending:
            after_id, (due, _seq, callback) = min(self.pending.items(), key=lambda entry: (entry[1][0], entry[1][1]))
            if due > end_ms:
                break
            del self.pending[after_id]
            self.now = due
            callback()
        self.now = max(self.now, end_ms)


def make_context(seed: int = 0, width: int = 1920, height: int = 1080, profile: str = DEFAULT_PROFILE) -> EffectContext:
    """EffectContext d'un écran de test."""
    return EffectContext(width=width, height=height, rng=random.Random(seed), profile=get_profile(profile))


def blank_image(width: int = 1920, height: int = 1080) -> QImage:
    image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(QColor(0, 0, 0, 0))
    return image


def render(malus: Malus, elapsed_ms: int) -> QImage:
    """Dessine le malus à l'instant `elapsed_ms` sur une image transparente de la taille de l'écran."""
    image = blank_image(malus.ctx.width, malus.ctx.height)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    malus.render(painter, elapsed_ms)
    painter.end()
    return image


def painted_pixels(image: QImage, step: int = 8) -> int:
    """Nombre de pixels non transparents (échantillonnés tous les `step` px)."""
    return sum(
        1
        for x in range(0, image.width(), step)
        for y in range(0, image.height(), step)
        if image.pixelColor(x, y).alpha() > 0
    )


def color_at(image: QImage, x: float, y: float) -> QColor:
    return image.pixelColor(int(x), int(y))
