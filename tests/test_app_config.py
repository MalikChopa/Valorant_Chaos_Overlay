"""Logique de ChaosApp liée à la config, testée sans fenêtre (faux objets à la place de Tk)."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from chaos_overlay import app, config
from chaos_overlay.config import Config


class FakeVar:
    """Remplace tk.IntVar / tk.BooleanVar."""

    def __init__(self, value: Any) -> None:
        self.value = value

    def get(self) -> Any:
        return self.value

    def set(self, value: Any) -> None:
        self.value = value


def fake_app(tmp_path: Path, frequency: int, states: dict[str, bool]) -> SimpleNamespace:
    return SimpleNamespace(
        config=Config(),
        config_path=tmp_path / "chaos_config.json",
        timer_interval=FakeVar(frequency),
        malus_states={key: FakeVar(value) for key, value in states.items()},
    )


def test_save_config_writes_dashboard_values(tmp_path: Path) -> None:
    states = {key: True for key in Config().enabled}
    states["flashbang"] = False
    fake = fake_app(tmp_path, 25, states)
    assert app.ChaosApp.save_config(fake) is True  # type: ignore[arg-type]
    saved = config.load(fake.config_path)
    assert saved.frequency_s == 25
    assert saved.enabled == states


def test_save_config_clamps_frequency(tmp_path: Path) -> None:
    fake = fake_app(tmp_path, 99999, dict(Config().enabled))
    app.ChaosApp.save_config(fake)  # type: ignore[arg-type]
    assert fake.timer_interval.get() == 3600
    assert config.load(fake.config_path).frequency_s == 3600


def test_start_clicked_saves_then_starts_timer(tmp_path: Path) -> None:
    order: list[str] = []
    fake = SimpleNamespace(save_config=lambda: order.append("save"), start_timer=lambda: order.append("timer"))
    app.ChaosApp.start_clicked(fake)  # type: ignore[arg-type]
    assert order == ["save", "timer"]


def test_execute_malus_uses_configured_duration(monkeypatch: pytest.MonkeyPatch) -> None:
    received: list[int | None] = []

    class RecordingMalus:
        def __init__(self, duration_ms: int | None = None) -> None:
            received.append(duration_ms)

        def start(self, ctx: object) -> None:
            pass

    monkeypatch.setattr(app, "REGISTRY", {"flashbang": RecordingMalus})
    timer_calls: list[int] = []
    cfg = Config()
    cfg.durations_ms["flashbang"] = 4321
    fake = SimpleNamespace(
        config=cfg,
        overlay=SimpleNamespace(make_context=lambda rng: object()),
        rng=None,
        start_timer=lambda: timer_calls.append(1),
    )
    app.ChaosApp.execute_malus(fake, "flashbang")  # type: ignore[arg-type]
    app.ChaosApp.execute_malus(fake, "rien")  # type: ignore[arg-type]
    assert received == [4321]
    assert timer_calls == [1, 1]
