"""Tests de l'icône dessinée en code."""

from __future__ import annotations

import pytest
from PySide6.QtGui import QColor

from chaos_overlay import theme
from chaos_overlay.ui.icon import SIZES, app_icon, render_icon


@pytest.mark.parametrize("size", SIZES)
def test_icon_sizes(qapp: object, size: int) -> None:
    image = render_icon(size)
    assert (image.width(), image.height()) == (size, size)
    assert image.pixelColor(size // 2, size // 2) == QColor(theme.ACCENT)
    assert image.pixelColor(0, 0).alpha() == 0  # coins arrondis transparents


def test_paused_icon_is_grey(qapp: object) -> None:
    assert render_icon(64, paused=True).pixelColor(32, 32) == QColor(theme.DIM)


def test_app_icon_has_every_size(qapp: object) -> None:
    sizes = {(size.width(), size.height()) for size in app_icon().availableSizes()}
    assert {(size, size) for size in SIZES} <= sizes
