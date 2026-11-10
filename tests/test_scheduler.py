"""Tests de la logique pure : tirage, rythme de la roulette, fréquence saisie."""

from __future__ import annotations

import random

import pytest

from chaos_overlay import scheduler


def original_delays(spins_left: int = 30, delay: int = 50) -> list[int]:
    """Formule d'origine (animate_roulette, ligne 247) déroulée récursivement."""
    if spins_left <= 0:
        return []
    new_delay = delay + int(120 / spins_left)
    return [new_delay] + original_delays(spins_left - 1, new_delay)


def test_roulette_delays_match_original_formula() -> None:
    delays = scheduler.roulette_delays()
    assert len(delays) == 30
    assert delays == original_delays()


def test_roulette_delays_known_values() -> None:
    delays = scheduler.roulette_delays()
    assert delays[0] == 54  # 50 + int(120 / 30)
    assert delays[-1] == original_delays()[-1]
    assert delays == sorted(delays)  # la roulette ne fait que ralentir


def test_pick_with_seed_is_reproducible() -> None:
    active = ["flashbang", "scanlines", "mosquito"]
    assert scheduler.pick(active, random.Random(42)) == random.Random(42).choice(active)
    results = {scheduler.pick(active, random.Random(seed)) for seed in range(50)}
    assert results <= set(active)
    assert len(results) > 1


def test_pick_empty_returns_rien() -> None:
    assert scheduler.pick([], random.Random(1)) == "rien"
    assert scheduler.roulette_pool([]) == ["rien"]


def test_pick_consumes_rng_like_original() -> None:
    """L'ancien code faisait random.choice(["rien"]) : même consommation du hasard."""
    rng_new, rng_old = random.Random(7), random.Random(7)
    scheduler.pick([], rng_new)
    rng_old.choice(["rien"])
    assert rng_new.random() == rng_old.random()


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("60", 60),
        ("1", 1),
        ("007", 7),
        ("3600", 3600),
        ("0", None),
        ("", None),
        ("-5", None),
        ("abc", None),
        ("1.5", None),
        (" 5", None),
        ("5 ", None),
        ("²", None),  # chiffre Unicode : l'ancien code plantait sur int("²")
        ("٣", None),  # chiffre arabe-indien
    ],
)
def test_parse_frequency(text: str, expected: int | None) -> None:
    assert scheduler.parse_frequency(text) == expected


def test_display_name() -> None:
    assert scheduler.display_name("tunnel_vision") == "TUNNEL VISION"
    assert scheduler.display_name("rien") == "RIEN"
