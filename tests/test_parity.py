"""Parité avec l'ancien code : mêmes appels au canvas, aux mêmes instants, avec le même hasard.

L'ancien code (tests/legacy_reference.py, copie verbatim) et le nouveau tournent sur le même
faux canvas / faux minuteur ; on compare la liste complète des appels (création, coordonnées,
couleurs, polices, textes, effacements, avec leur instant en ms).
"""

from __future__ import annotations

import random
from pathlib import Path

import pytest
from fakes import FakeCanvas, FakeClock, FakeRoot, make_context
from legacy_reference import LegacyOverlay

from chaos_overlay import scheduler
from chaos_overlay.malus import REGISTRY, mlg_gif
from chaos_overlay.ui.roulette import RouletteView

SCREENS = [(1920, 1080), (2560, 1440), (1280, 720)]
SEEDS = [0, 1, 2, 3, 12345]
END_MS = 15000


def legacy_method_name(key: str) -> str:
    return "effect_mlg_gif" if key == "mlg_fullscreen" else f"effect_{key}"


def run_legacy(key: str, seed: int, width: int, height: int, gif_frames: list[str]) -> FakeCanvas:
    clock = FakeClock()
    canvas = FakeCanvas(clock)
    legacy = LegacyOverlay(FakeRoot(clock), canvas, width, height, gif_frames=list(gif_frames))
    random.seed(seed)
    getattr(legacy, legacy_method_name(key))()
    clock.run_until(END_MS)
    return canvas


def run_new(key: str, seed: int, width: int, height: int) -> FakeCanvas:
    clock = FakeClock()
    canvas = FakeCanvas(clock)
    REGISTRY[key]().start(make_context(clock, canvas, seed=seed, width=width, height=height))
    clock.run_until(END_MS)
    return canvas


def install_fake_gif(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, frames: list[str]) -> None:
    (tmp_path / "mlg.gif").write_bytes(b"GIF89a fake")
    monkeypatch.setattr(mlg_gif, "resource_path", lambda name: tmp_path / name)
    monkeypatch.setattr(mlg_gif, "load_frames", lambda path, max_frames, master: frames[:max_frames])
    monkeypatch.setattr(mlg_gif, "_frame_cache", {})


@pytest.mark.parametrize("key", list(REGISTRY))
@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize(("width", "height"), SCREENS)
def test_effect_parity(
    key: str, seed: int, width: int, height: int, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Ancien code : toutes les images du GIF (~608) ; nouveau : 150 au plus.
    all_frames = [f"frame{index}" for index in range(608)]
    install_fake_gif(monkeypatch, tmp_path, all_frames)
    legacy = run_legacy(key, seed, width, height, all_frames)
    new = run_new(key, seed, width, height)
    assert new.calls == legacy.calls
    assert legacy.calls, "aucun appel enregistré : test vide"
    assert new.alive == set()


def test_gif_parity_short_gif_loops(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """GIF plus court que l'effet : les deux versions bouclent pareil."""
    frames = [f"frame{index}" for index in range(7)]
    install_fake_gif(monkeypatch, tmp_path, frames)
    assert run_new("mlg_fullscreen", 0, 1920, 1080).calls == run_legacy("mlg_fullscreen", 0, 1920, 1080, frames).calls


def test_gif_parity_missing_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(mlg_gif, "resource_path", lambda name: tmp_path / "absent.gif")
    monkeypatch.setattr(mlg_gif, "_frame_cache", {})
    assert run_new("mlg_fullscreen", 0, 1920, 1080).calls == []
    assert run_legacy("mlg_fullscreen", 0, 1920, 1080, []).calls == []


def test_gif_never_shows_frame_150_in_old_code(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Justifie la limite de 150 images : l'ancien code n'affichait jamais l'image d'indice >= 150."""
    all_frames = [f"frame{index}" for index in range(608)]
    legacy = run_legacy("mlg_fullscreen", 0, 1920, 1080, all_frames)
    shown = {value for call in legacy.calls if call[1] in ("itemconfig", "image") for name, value in call[-1] if name == "image"}
    assert max(int(frame.removeprefix("frame")) for frame in shown) == 149


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize(
    "active",
    [list(REGISTRY), ["flashbang"], ["scanlines", "mosquito", "paranoia"], []],
)
def test_roulette_parity(seed: int, active: list[str]) -> None:
    # Ancien code : trigger_malus (lignes 231-234) puis start_roulette_ui.
    old_clock = FakeClock()
    old_canvas = FakeCanvas(old_clock)
    legacy = LegacyOverlay(FakeRoot(old_clock), old_canvas, 1920, 1080)
    random.seed(seed)
    old_active = active if active else ["rien"]
    legacy.start_roulette_ui(random.choice(old_active), old_active)
    old_clock.run_until(60000)

    # Nouveau code : scheduler.pick + RouletteView.
    new_clock = FakeClock()
    new_canvas = FakeCanvas(new_clock)
    rng = random.Random(seed)
    executed: list[tuple[int, str]] = []
    final_key = scheduler.pick(active, rng)
    view = RouletteView(new_canvas, new_clock.after, rng, 1080)  # type: ignore[arg-type]
    view.spin(final_key, scheduler.roulette_pool(active), on_done=lambda key: executed.append((new_clock.now, key)))
    new_clock.run_until(60000)

    assert new_canvas.calls == old_canvas.calls
    assert [key for _, key in executed] == legacy.executed
    assert new_canvas.alive == set()
    # Instant du malus : somme des 30 délais + 1,5 s de pause sur le résultat.
    assert executed[0][0] == sum(scheduler.roulette_delays()) + 1500
