"""Faux canvas et faux minuteur Tk pour tester les malus sans fenêtre."""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any

from chaos_overlay.malus.base import EffectContext


def _flatten(values: tuple[Any, ...]) -> tuple[Any, ...]:
    """Aplati les coordonnées comme tkinter : f([1, 2], 3) et f(1, 2, 3) donnent le même appel."""
    flat: list[Any] = []
    for value in values:
        if isinstance(value, (list, tuple)):
            flat.extend(_flatten(tuple(value)))
        else:
            flat.append(value)
    return tuple(flat)


class FakeCanvas:
    """Enregistre chaque appel (avec l'heure du faux minuteur) au lieu de dessiner."""

    def __init__(self, clock: "FakeClock | None" = None) -> None:
        self.clock = clock
        self.calls: list[tuple[Any, ...]] = []
        self.alive: set[int] = set()
        self.deleted: list[int] = []
        self._next_id = 1

    def _now(self) -> int:
        return self.clock.now if self.clock is not None else 0

    def _create(self, kind: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> int:
        item = self._next_id
        self._next_id += 1
        self.alive.add(item)
        self.calls.append((self._now(), kind, item, _flatten(args), sorted(kwargs.items())))
        return item

    def create_rectangle(self, *args: Any, **kwargs: Any) -> int:
        return self._create("rectangle", args, kwargs)

    def create_oval(self, *args: Any, **kwargs: Any) -> int:
        return self._create("oval", args, kwargs)

    def create_polygon(self, *args: Any, **kwargs: Any) -> int:
        return self._create("polygon", args, kwargs)

    def create_line(self, *args: Any, **kwargs: Any) -> int:
        return self._create("line", args, kwargs)

    def create_text(self, *args: Any, **kwargs: Any) -> int:
        return self._create("text", args, kwargs)

    def create_image(self, *args: Any, **kwargs: Any) -> int:
        return self._create("image", args, kwargs)

    def delete(self, item: int) -> None:
        self.alive.discard(item)
        self.deleted.append(item)
        self.calls.append((self._now(), "delete", item))

    def coords(self, item: int, *args: Any) -> None:
        self.calls.append((self._now(), "coords", item, _flatten(args)))

    def itemconfig(self, item: int, **kwargs: Any) -> None:
        self.calls.append((self._now(), "itemconfig", item, sorted(kwargs.items())))


class FakeClock:
    """Faux `after` / `after_cancel` : un temps virtuel en ms qu'on fait avancer à la main.

    À échéance égale, les rappels tournent dans l'ordre où ils ont été programmés (comme Tk).
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


class FakeRoot:
    """Imite root.after pour l'ancien code (qui appelle self.root.after)."""

    def __init__(self, clock: FakeClock) -> None:
        self.after = clock.after
        self.after_cancel = clock.after_cancel


def make_context(
    clock: FakeClock, canvas: FakeCanvas, seed: int = 0, width: int = 1920, height: int = 1080
) -> EffectContext:
    """EffectContext branché sur les faux (le typage strict ne s'applique pas aux tests)."""
    return EffectContext(
        canvas=canvas,  # type: ignore[arg-type]
        width=width,
        height=height,
        after=clock.after,
        after_cancel=clock.after_cancel,
        rng=random.Random(seed),
    )
