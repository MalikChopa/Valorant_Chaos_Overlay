"""Contrat commun des malus : contexte d'affichage, classe de base et registre."""

from __future__ import annotations

import random
import tkinter as tk
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import ClassVar, TypeVar


@dataclass
class EffectContext:
    """Ce dont un malus a besoin pour dessiner : le canvas de l'overlay et le minuteur Tk."""

    canvas: tk.Canvas
    width: int
    height: int
    after: Callable[[int, Callable[[], None]], str]
    after_cancel: Callable[[str], None]
    rng: random.Random


class Malus(ABC):
    """Un effet visuel. Une instance par déclenchement : elle garde ses propres éléments.

    Les sous-classes définissent `key`, `default_duration_ms` et `_draw()`.
    `start()` dessine puis programme `stop()` après la durée de l'effet.
    `stop()` efface tout ce que l'instance a créé ; on peut l'appeler plusieurs fois.
    """

    key: ClassVar[str]
    default_duration_ms: ClassVar[int]

    def __init__(self, duration_ms: int | None = None) -> None:
        if duration_ms is None:
            duration_ms = self.default_duration_ms
        self.duration_ms = duration_ms
        self._ctx: EffectContext | None = None
        self._items: list[int] = []
        self._pending_after_ids: set[str] = set()
        self._stopped = False

    @property
    def is_running(self) -> bool:
        """Vrai entre start() et stop()."""
        return self._ctx is not None and not self._stopped

    def start(self, ctx: EffectContext) -> None:
        """Affiche l'effet et programme sa fin."""
        if self._ctx is not None:
            raise RuntimeError("Une instance de malus ne sert qu'une fois : crée-en une nouvelle.")
        self._ctx = ctx
        self._draw(ctx)
        self._schedule(self.duration_ms, self.stop)

    def stop(self) -> None:
        """Annule les minuteurs en attente et efface les éléments du canvas (idempotent)."""
        if self._stopped:
            return
        self._stopped = True
        ctx = self._ctx
        if ctx is None:
            return
        for after_id in list(self._pending_after_ids):
            ctx.after_cancel(after_id)
        self._pending_after_ids.clear()
        for item in self._items:
            ctx.canvas.delete(item)
        self._items.clear()

    @abstractmethod
    def _draw(self, ctx: EffectContext) -> None:
        """Crée les éléments de l'effet (avec `_track`) et lance l'animation éventuelle."""

    def _track(self, item: int) -> int:
        """Retient un élément du canvas pour l'effacer au stop()."""
        self._items.append(item)
        return item

    def _schedule(self, delay_ms: int, callback: Callable[[], None]) -> None:
        """Programme `callback` dans `delay_ms` ms ; stop() l'annule s'il n'a pas encore tourné."""
        ctx = self._ctx
        if ctx is None or self._stopped:
            return
        # La liste sert de boîte : on connaît l'id seulement après l'appel à after().
        id_box: list[str] = []

        def run() -> None:
            self._pending_after_ids.discard(id_box[0])
            if not self._stopped:
                callback()

        after_id = ctx.after(delay_ms, run)
        id_box.append(after_id)
        self._pending_after_ids.add(after_id)


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
