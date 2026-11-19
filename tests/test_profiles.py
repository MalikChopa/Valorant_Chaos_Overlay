"""Tests des profils de jeu : zones valides, clé inconnue."""

from __future__ import annotations

import pytest

from chaos_overlay.profiles import DEFAULT_PROFILE, PROFILES, get_profile


@pytest.mark.parametrize("key", list(PROFILES))
def test_zones_are_inside_the_screen(key: str) -> None:
    profile = PROFILES[key]
    assert profile.key == key
    assert profile.name
    assert profile.hud_zones
    for x0, y0, x1, y1 in profile.hud_zones:
        assert 0.0 <= x0 < x1 <= 1.0
        assert 0.0 <= y0 < y1 <= 1.0


@pytest.mark.parametrize("key", list(PROFILES))
def test_zones_never_cover_the_crosshair(key: str) -> None:
    """Le HUD masqué ne doit jamais cacher le centre : c'est le rôle d'autres malus."""
    for x0, y0, x1, y1 in PROFILES[key].hud_zones:
        assert not (x0 <= 0.5 <= x1 and y0 <= 0.5 <= y1)


def test_generic_is_first_and_default() -> None:
    assert next(iter(PROFILES)) == DEFAULT_PROFILE == "generic"


def test_unknown_key_gives_generic() -> None:
    assert get_profile("pong").key == "generic"
    assert get_profile("cs2").name == "Counter-Strike 2"
