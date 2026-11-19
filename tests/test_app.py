"""Tests de ChaosApp : réglages, minuteur, roulette puis malus (faux minuteur, fausse horloge)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fakes import FakeClock
from pytestqt.qtbot import QtBot

from chaos_overlay import app
from chaos_overlay.config import Config


class FakeHotkey:
    def __init__(self, ok: bool = True) -> None:
        self.ok = ok
        self.started = False
        self.stopped = False

    def start(self) -> bool:
        self.started = True
        return self.ok

    def stop(self) -> None:
        self.stopped = True


@pytest.fixture
def chaos(qtbot: QtBot, tmp_path: Path) -> tuple[app.ChaosApp, FakeClock, FakeHotkey]:
    clock = FakeClock()
    hotkey = FakeHotkey()
    chaos_app = app.ChaosApp(
        config_path=tmp_path / "chaos_config.json",
        after=clock.after,
        clock=lambda: clock.now,
        hotkey=hotkey,  # type: ignore[arg-type]
    )
    qtbot.addWidget(chaos_app.dashboard)
    qtbot.addWidget(chaos_app.overlay)
    return chaos_app, clock, hotkey


def test_start_saves_dashboard_values_and_starts_timer(chaos: tuple[app.ChaosApp, FakeClock, FakeHotkey]) -> None:
    chaos_app, _, _ = chaos
    chaos_app.dashboard.frequency.setValue(25)
    chaos_app.dashboard.rows["flashbang"].checkbox.setChecked(False)
    chaos_app.dashboard.profile_box.setCurrentIndex(chaos_app.dashboard.profile_box.findData("cs2"))
    chaos_app.start_clicked()

    saved = json.loads(chaos_app.config_path.read_text(encoding="utf-8"))
    assert saved["frequency_s"] == 25
    assert saved["enabled"]["flashbang"] is False
    assert saved["profile"] == "cs2"
    assert chaos_app.chaos_timer.isActive()
    assert chaos_app.chaos_timer.interval() == 25000
    assert chaos_app.overlay.isVisible()


def test_existing_config_is_loaded(qtbot: QtBot, tmp_path: Path) -> None:
    path = tmp_path / "chaos_config.json"
    path.write_text(json.dumps({"frequency_s": 90, "profile": "apex"}), encoding="utf-8")
    chaos_app = app.ChaosApp(config_path=path, hotkey=FakeHotkey())  # type: ignore[arg-type]
    qtbot.addWidget(chaos_app.dashboard)
    assert chaos_app.dashboard.frequency.value() == 90
    assert chaos_app.dashboard.profile_box.currentData() == "apex"


def test_trigger_spins_roulette_then_starts_malus_with_configured_duration(
    chaos: tuple[app.ChaosApp, FakeClock, FakeHotkey],
) -> None:
    chaos_app, clock, _ = chaos
    chaos_app.config = Config(enabled={key: key == "low_hp" for key in Config().enabled})
    chaos_app.config.durations_ms["low_hp"] = 1234
    chaos_app.running = True
    chaos_app.trigger_malus()
    assert chaos_app.roulette.visible
    assert chaos_app.overlay.effects == []

    clock.run_until(60000)
    assert [item.malus.key for item in chaos_app.overlay.effects] == ["low_hp"]
    assert chaos_app.overlay.effects[0].malus.duration_ms == 1234
    assert chaos_app.chaos_timer.isActive(), "le minuteur doit repartir après le malus"


def test_nothing_checked_draws_rien_and_continues(chaos: tuple[app.ChaosApp, FakeClock, FakeHotkey]) -> None:
    chaos_app, clock, _ = chaos
    chaos_app.config = Config(enabled={key: False for key in Config().enabled})
    chaos_app.running = True
    chaos_app.trigger_malus()
    clock.run_until(60000)
    assert chaos_app.overlay.effects == []
    assert chaos_app.chaos_timer.isActive()


def test_crashing_malus_does_not_stop_the_chaos(
    chaos: tuple[app.ChaosApp, FakeClock, FakeHotkey], monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    chaos_app, _, _ = chaos

    def boom(*args: object) -> None:
        raise RuntimeError("boom de test")

    monkeypatch.setattr(chaos_app.overlay, "add_effect", boom)
    chaos_app.running = True
    chaos_app.execute_malus("flashbang")
    assert "flashbang" in caplog.text
    assert chaos_app.chaos_timer.isActive()


def test_quit_stops_timer_and_close_releases_hotkey(chaos: tuple[app.ChaosApp, FakeClock, FakeHotkey]) -> None:
    chaos_app, _, hotkey = chaos
    chaos_app.start_clicked()
    chaos_app.quit_clicked()
    assert not chaos_app.chaos_timer.isActive()
    chaos_app.close()
    assert hotkey.stopped


def test_launch_warns_when_home_is_taken(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    warnings: list[str] = []
    monkeypatch.setattr(app.QMessageBox, "warning", lambda parent, title, text: warnings.append(text))
    chaos_app = app.ChaosApp(config_path=tmp_path / "c.json", hotkey=FakeHotkey(ok=False))  # type: ignore[arg-type]
    qtbot.addWidget(chaos_app.dashboard)
    qtbot.addWidget(chaos_app.overlay)
    chaos_app.launch()
    assert warnings == [app.HOTKEY_WARNING]
    assert chaos_app.overlay.isVisible()
    assert chaos_app.splash is not None
    qtbot.waitUntil(chaos_app.dashboard.isVisible, timeout=5000)


def test_screen_for_unknown_index_is_primary(qapp: object) -> None:
    assert app.ChaosApp.screen_for(99) is not None


def test_timer_does_not_run_before_start(chaos: tuple[app.ChaosApp, FakeClock, FakeHotkey]) -> None:
    chaos_app, _, _ = chaos
    chaos_app.start_timer()
    assert not chaos_app.chaos_timer.isActive()
    assert chaos_app.status_text() == "Chaos à l'arrêt"


def test_pause_keeps_the_countdown_and_resume_restarts_it(chaos: tuple[app.ChaosApp, FakeClock, FakeHotkey]) -> None:
    chaos_app, _, _ = chaos
    chaos_app.dashboard.frequency.setValue(120)
    chaos_app.start_clicked()
    assert chaos_app.status_text().startswith("Prochain malus dans 1")

    chaos_app.toggle_pause()
    assert chaos_app.paused and not chaos_app.chaos_timer.isActive()
    assert chaos_app.status_text() == "Chaos en pause"
    assert chaos_app.tray.pause_action.text() == "Reprendre le chaos"
    chaos_app.start_timer()  # le minuteur reste arrêté en pause
    assert not chaos_app.chaos_timer.isActive()

    chaos_app.toggle_pause()
    assert not chaos_app.paused and chaos_app.chaos_timer.isActive()
    assert 110_000 < chaos_app.chaos_timer.remainingTime() <= 120_000
    assert chaos_app.tray.pause_action.text() == "Mettre en pause"


def test_pause_is_ignored_before_start(chaos: tuple[app.ChaosApp, FakeClock, FakeHotkey]) -> None:
    chaos_app, _, _ = chaos
    chaos_app.toggle_pause()
    assert not chaos_app.paused
    assert not chaos_app.tray.pause_action.isEnabled()


def test_trigger_now_spins_immediately_once(chaos: tuple[app.ChaosApp, FakeClock, FakeHotkey]) -> None:
    chaos_app, clock, _ = chaos
    chaos_app.start_clicked()
    chaos_app.trigger_now()
    assert chaos_app.roulette.visible
    assert not chaos_app.chaos_timer.isActive()
    assert chaos_app.status_text() == "Roulette en cours..."
    pending = len(clock.pending)
    chaos_app.trigger_now()  # ignoré : la roulette tourne déjà
    assert len(clock.pending) == pending
    clock.run_until(60000)
    assert chaos_app.chaos_timer.isActive()


def test_preview_shows_malus_without_roulette_or_timer(chaos: tuple[app.ChaosApp, FakeClock, FakeHotkey]) -> None:
    chaos_app, _, _ = chaos
    chaos_app.dashboard.rows["sniper_scope"].duration.setValue(2.0)
    chaos_app.dashboard.preview_requested.emit("sniper_scope")
    assert [item.malus.key for item in chaos_app.overlay.effects] == ["sniper_scope"]
    assert chaos_app.overlay.effects[0].malus.duration_ms == 2000
    assert not chaos_app.roulette.visible
    assert not chaos_app.chaos_timer.isActive()
    assert chaos_app.overlay.isVisible()


def test_tray_menu_is_wired(chaos: tuple[app.ChaosApp, FakeClock, FakeHotkey]) -> None:
    chaos_app, _, _ = chaos
    chaos_app.tray.open_action.trigger()
    assert chaos_app.dashboard.isVisible()
    chaos_app.start_clicked()
    chaos_app.tray.pause_action.trigger()
    assert chaos_app.paused
    chaos_app.tray.trigger_action.trigger()
    assert chaos_app.roulette.visible


def test_status_is_shown_in_dashboard_and_tray(chaos: tuple[app.ChaosApp, FakeClock, FakeHotkey]) -> None:
    chaos_app, _, _ = chaos
    chaos_app.start_clicked()
    chaos_app.refresh_status()
    assert chaos_app.dashboard.status.text().startswith("Prochain malus dans")
    assert chaos_app.dashboard.status.text() in chaos_app.tray.toolTip()
