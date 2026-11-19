"""Tests du Dashboard : champs remplis depuis la config, relus, boutons."""

from __future__ import annotations

from pytestqt.qtbot import QtBot

from chaos_overlay.config import Config
from chaos_overlay.malus import REGISTRY
from chaos_overlay.profiles import PROFILES
from chaos_overlay.ui.dashboard import Dashboard


def make_dashboard(qtbot: QtBot, cfg: Config | None = None) -> Dashboard:
    dashboard = Dashboard(cfg or Config(), REGISTRY, PROFILES, ["Écran 1", "Écran 2"])
    qtbot.addWidget(dashboard)
    return dashboard


def test_round_trip_keeps_config(qtbot: QtBot) -> None:
    cfg = Config(frequency_s=42, profile="apex", screen=1)
    cfg.enabled["mosquito"] = False
    cfg.durations_ms["flashbang"] = 3500
    assert make_dashboard(qtbot, cfg).to_config() == cfg


def test_rows_follow_registry_order(qtbot: QtBot) -> None:
    dashboard = make_dashboard(qtbot)
    assert list(dashboard.rows) == list(REGISTRY)
    assert dashboard.rows["low_hp"].checkbox.toolTip() == REGISTRY["low_hp"].description


def test_edits_are_read_back(qtbot: QtBot) -> None:
    dashboard = make_dashboard(qtbot)
    dashboard.frequency.setValue(15)
    dashboard.profile_box.setCurrentIndex(dashboard.profile_box.findData("overwatch2"))
    dashboard.rows["scanlines"].checkbox.setChecked(False)
    dashboard.rows["sniper_scope"].duration.setValue(4.5)
    cfg = dashboard.to_config()
    assert cfg.frequency_s == 15
    assert cfg.profile == "overwatch2"
    assert cfg.enabled["scanlines"] is False
    assert cfg.durations_ms["sniper_scope"] == 4500


def test_widgets_enforce_bounds(qtbot: QtBot) -> None:
    dashboard = make_dashboard(qtbot)
    dashboard.frequency.setValue(0)
    dashboard.rows["flashbang"].duration.setValue(999)
    cfg = dashboard.to_config()
    assert cfg.frequency_s == 1
    assert cfg.durations_ms["flashbang"] == 60000


def test_unknown_screen_falls_back_to_first(qtbot: QtBot) -> None:
    assert make_dashboard(qtbot, Config(screen=7)).to_config().screen == 0


def test_select_all_and_none(qtbot: QtBot) -> None:
    dashboard = make_dashboard(qtbot)
    dashboard.set_all(False)
    assert not any(dashboard.to_config().enabled.values())
    dashboard.set_all(True)
    assert all(dashboard.to_config().enabled.values())


def test_start_hides_and_emits(qtbot: QtBot) -> None:
    dashboard = make_dashboard(qtbot)
    dashboard.open()
    assert dashboard.isVisible()
    with qtbot.waitSignal(dashboard.start_requested, timeout=1000):
        dashboard.start_button.click()
    assert not dashboard.isVisible()


def test_quit_emits(qtbot: QtBot) -> None:
    dashboard = make_dashboard(qtbot)
    with qtbot.waitSignal(dashboard.quit_requested, timeout=1000):
        dashboard.quit_button.click()


def test_close_only_hides(qtbot: QtBot) -> None:
    dashboard = make_dashboard(qtbot)
    dashboard.open()
    dashboard.close()
    assert not dashboard.isVisible()
    dashboard.open()
    assert dashboard.isVisible()


def test_test_button_requests_preview(qtbot: QtBot) -> None:
    dashboard = make_dashboard(qtbot)
    with qtbot.waitSignal(dashboard.preview_requested, timeout=1000) as blocker:
        dashboard.rows["low_hp"].test_button.click()
    assert blocker.args == ["low_hp"]


def test_status_line(qtbot: QtBot) -> None:
    dashboard = make_dashboard(qtbot)
    dashboard.set_status("Chaos en pause")
    assert dashboard.status.text() == "Chaos en pause"
