"""Tests de la fenêtre d'overlay : malus actifs, nettoyage, animation seulement si besoin."""

from __future__ import annotations

import random

from fakes import blank_image, painted_pixels
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter

from chaos_overlay.malus import REGISTRY
from chaos_overlay.profiles import get_profile
from chaos_overlay.ui.overlay import OverlayWindow


class ManualClock:
    def __init__(self) -> None:
        self.now = 0

    def __call__(self) -> int:
        return self.now


def make_overlay() -> tuple[OverlayWindow, ManualClock]:
    clock = ManualClock()
    overlay = OverlayWindow(clock)
    overlay.resize(1920, 1080)
    return overlay, clock


def frame(overlay: OverlayWindow, now: int) -> int:
    image = blank_image()
    painter = QPainter(image)
    overlay.paint_frame(painter, now)
    painter.end()
    return painted_pixels(image)


def test_window_is_passive(qapp: object) -> None:
    overlay, _ = make_overlay()
    flags = overlay.windowFlags()
    assert flags & Qt.WindowType.WindowTransparentForInput
    assert flags & Qt.WindowType.WindowStaysOnTopHint
    assert flags & Qt.WindowType.FramelessWindowHint
    assert flags & Qt.WindowType.WindowDoesNotAcceptFocus
    assert overlay.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    assert overlay.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)


def test_context_uses_window_size_and_profile(qapp: object) -> None:
    overlay, _ = make_overlay()
    ctx = overlay.context(random.Random(0), get_profile("cs2"))
    assert (ctx.width, ctx.height, ctx.profile.key) == (1920, 1080, "cs2")


def test_effects_overlap_and_are_removed_when_finished(qapp: object) -> None:
    overlay, clock = make_overlay()
    ctx = overlay.context(random.Random(0), get_profile("generic"))
    assert not overlay.is_animating
    assert frame(overlay, 0) == 0

    overlay.add_effect(REGISTRY["blind_spot"](ctx))  # 8 s
    clock.now = 1000
    overlay.add_effect(REGISTRY["tunnel_vision"](ctx))  # 8 s
    assert overlay.is_animating
    assert len(overlay.effects) == 2
    assert frame(overlay, 4000) > 0

    clock.now = 8500
    overlay.prune()
    assert [item.malus.key for item in overlay.effects] == ["tunnel_vision"]
    clock.now = 9000
    overlay._on_frame()
    assert overlay.effects == []
    assert not overlay.is_animating, "l'animation doit s'arrêter au repos"
    assert frame(overlay, 9000) == 0


def test_animation_keeps_running_while_roulette_is_visible(qapp: object) -> None:
    overlay, _ = make_overlay()

    class Visible:
        visible = True

    overlay.roulette = Visible()  # type: ignore[assignment]
    overlay.wake()
    overlay._on_frame()
    assert overlay.is_animating
