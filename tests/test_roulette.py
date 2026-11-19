"""Tests de la roulette : rythme, textes affichés, résultat, avec un faux minuteur."""

from __future__ import annotations

import random

import pytest
from fakes import FakeClock, blank_image, painted_pixels
from PySide6.QtGui import QPainter

from chaos_overlay import scheduler
from chaos_overlay.malus import REGISTRY, label_of
from chaos_overlay.ui.roulette import Roulette, paint_roulette


def spin(active: list[str], seed: int = 0) -> tuple[FakeClock, Roulette, list[str], list[tuple[int, str]]]:
    clock = FakeClock()
    rng = random.Random(seed)
    texts: list[str] = []
    done: list[tuple[int, str]] = []
    roulette = Roulette(clock.after, rng, label_of)
    roulette.on_change = lambda: texts.append(roulette.text)
    final = scheduler.pick(active, rng)
    roulette.spin(final, scheduler.roulette_pool(active), on_done=lambda key: done.append((clock.now, key)))
    return clock, roulette, texts, done


@pytest.mark.parametrize("active", [list(REGISTRY), ["flashbang"], []])
def test_roulette_spins_30_times_then_shows_result(active: list[str]) -> None:
    clock, roulette, texts, done = spin(active)
    assert roulette.visible
    clock.run_until(60000)
    pool_labels = {label_of(key).upper() for key in scheduler.roulette_pool(active)}
    assert len(texts) == 30 + 1 + 1  # 30 noms, le résultat, puis l'effacement
    assert set(texts[:30]) <= pool_labels
    final_key = done[0][1]
    assert texts[30] == f">> {label_of(final_key).upper()} <<"
    assert texts[31] == ""
    assert not roulette.visible
    # Instant du malus : somme des 30 délais + 1,5 s de pause sur le résultat (comme la v2).
    assert done[0][0] == sum(scheduler.roulette_delays()) + scheduler.ROULETTE_RESULT_PAUSE_MS


def test_empty_selection_draws_rien() -> None:
    clock, _, texts, done = spin([])
    clock.run_until(60000)
    assert done[0][1] == scheduler.NOTHING
    assert texts[30] == ">> RIEN <<"


def test_paint_only_when_visible(qapp: object) -> None:
    clock, roulette, _, _ = spin(["flashbang"])
    image = blank_image()
    painter = QPainter(image)
    paint_roulette(painter, roulette, 1.0, 1080)
    painter.end()
    assert painted_pixels(image) > 0

    clock.run_until(60000)
    hidden = blank_image()
    painter = QPainter(hidden)
    paint_roulette(painter, roulette, 1.0, 1080)
    painter.end()
    assert painted_pixels(hidden) == 0
