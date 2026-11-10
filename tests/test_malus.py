"""Tests des malus avec un faux canvas : nettoyage, chevauchement, GIF paresseux."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest
from fakes import FakeCanvas, FakeClock, make_context

from chaos_overlay.malus import REGISTRY, mlg_gif
from chaos_overlay.malus.mosquito import Mosquito

ALL_KEYS = list(REGISTRY)


@pytest.fixture
def fake_gif(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> list[tuple[Path, int]]:
    """Remplace mlg.gif par un faux fichier et le chargement Tk par de fausses images.

    Renvoie la liste des appels à load_frames (chemin, nombre d'images demandées).
    """
    gif_file = tmp_path / "mlg.gif"
    gif_file.write_bytes(b"GIF89a fake")
    load_calls: list[tuple[Path, int]] = []

    def fake_load_frames(gif_path: Path, max_frames: int, master: object) -> list[str]:
        load_calls.append((gif_path, max_frames))
        return [f"frame{index}" for index in range(min(max_frames, 600))]

    monkeypatch.setattr(mlg_gif, "resource_path", lambda name: tmp_path / name)
    monkeypatch.setattr(mlg_gif, "load_frames", fake_load_frames)
    monkeypatch.setattr(mlg_gif, "_frame_cache", {})
    return load_calls


@pytest.mark.parametrize("key", ALL_KEYS)
def test_stop_removes_everything_and_is_idempotent(key: str, fake_gif: object) -> None:
    clock, canvas = FakeClock(), FakeCanvas()
    malus = REGISTRY[key]()
    malus.start(make_context(clock, canvas))
    assert canvas.alive, "le malus n'a rien dessiné"
    assert clock.pending, "aucun minuteur programmé"
    assert malus.is_running

    malus.stop()
    assert canvas.alive == set()
    assert clock.pending == {}
    assert not malus.is_running
    calls_after_first_stop = len(canvas.calls)
    cancelled_after_first_stop = len(clock.cancelled)

    malus.stop()
    assert len(canvas.calls) == calls_after_first_stop
    assert len(clock.cancelled) == cancelled_after_first_stop


@pytest.mark.parametrize("key", ALL_KEYS)
def test_effect_cleans_itself_after_its_duration(key: str, fake_gif: object) -> None:
    clock, canvas = FakeClock(), FakeCanvas()
    malus = REGISTRY[key]()
    malus.start(make_context(clock, canvas))
    clock.run_until(malus.duration_ms - 1)
    assert canvas.alive, "effacé trop tôt"
    clock.run_until(malus.duration_ms)
    assert canvas.alive == set()
    assert clock.pending == {}
    malus.stop()  # un stop() manuel après la fin ne change rien
    assert canvas.alive == set()


def test_stop_before_start_does_nothing() -> None:
    malus = REGISTRY["flashbang"]()
    malus.stop()
    malus.stop()
    assert not malus.is_running


def test_instance_cannot_start_twice() -> None:
    clock, canvas = FakeClock(), FakeCanvas()
    malus = REGISTRY["flashbang"]()
    malus.start(make_context(clock, canvas))
    with pytest.raises(RuntimeError):
        malus.start(make_context(clock, canvas))


def test_custom_duration() -> None:
    clock, canvas = FakeClock(), FakeCanvas()
    malus = REGISTRY["flashbang"](duration_ms=500)
    malus.start(make_context(clock, canvas))
    clock.run_until(500)
    assert canvas.alive == set()


def test_two_mosquitoes_overlap_without_sharing_state() -> None:
    """Bug d'origine : un 2e moustique écrasait self.mosq_* du 1er, qui restait à l'écran."""
    clock, canvas = FakeClock(), FakeCanvas()
    first = Mosquito()
    first.start(make_context(clock, canvas, seed=1))
    clock.run_until(3000)
    second = Mosquito()
    second.start(make_context(clock, canvas, seed=2))
    assert first.square != second.square
    assert len(canvas.alive) == 2

    clock.run_until(10000)  # fin du premier
    assert canvas.alive == {second.square}
    clock.run_until(13000)  # fin du second
    assert canvas.alive == set()
    assert clock.pending == {}


def test_two_gifs_overlap_and_clean_up(fake_gif: list[tuple[Path, int]]) -> None:
    clock, canvas = FakeClock(), FakeCanvas()
    first = REGISTRY["mlg_fullscreen"]()
    first.start(make_context(clock, canvas))
    clock.run_until(2000)
    second = REGISTRY["mlg_fullscreen"]()
    second.start(make_context(clock, canvas))
    assert len(canvas.alive) == 2
    clock.run_until(6000)
    assert len(canvas.alive) == 1
    clock.run_until(8000)
    assert canvas.alive == set()
    assert clock.pending == {}


def test_gif_frames_needed() -> None:
    assert mlg_gif.frames_needed(6000) == 150
    assert mlg_gif.frames_needed(6001) == 151
    assert mlg_gif.frames_needed(40) == 1


def test_gif_loads_lazily_once_and_only_150_frames(fake_gif: list[tuple[Path, int]]) -> None:
    import chaos_overlay.malus  # noqa: F401  (l'import seul ne charge rien)

    assert fake_gif == []
    clock, canvas = FakeClock(), FakeCanvas()
    REGISTRY["mlg_fullscreen"]().start(make_context(clock, canvas))
    assert len(fake_gif) == 1
    assert fake_gif[0][1] == 150
    clock.run_until(7000)
    REGISTRY["mlg_fullscreen"]().start(make_context(clock, canvas))
    assert len(fake_gif) == 1, "le GIF a été rechargé au lieu d'utiliser le cache"


def test_gif_missing_file_does_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(mlg_gif, "resource_path", lambda name: tmp_path / "absent.gif")
    monkeypatch.setattr(mlg_gif, "_frame_cache", {})
    clock, canvas = FakeClock(), FakeCanvas()
    malus = REGISTRY["mlg_fullscreen"]()
    with caplog.at_level(logging.WARNING):
        malus.start(make_context(clock, canvas))
    assert canvas.calls == []
    assert "introuvable" in caplog.text
    clock.run_until(10000)
    malus.stop()
    assert canvas.calls == []
