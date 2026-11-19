"""Tests de chaos_overlay.config : lecture tolérante, bornes, enregistrement atomique."""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from chaos_overlay import config, paths
from chaos_overlay.config import Config
from chaos_overlay.malus import REGISTRY

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DURATIONS = {key: cls.default_duration_ms for key, cls in REGISTRY.items()}


def write_json(path: Path, data: Any) -> Path:
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def warnings_of(caplog: pytest.LogCaptureFixture) -> list[str]:
    return [r.getMessage() for r in caplog.records if r.levelno >= logging.WARNING and r.name == config.__name__]


def test_defaults_follow_registry_order() -> None:
    cfg = Config()
    assert list(cfg.enabled) == list(REGISTRY)
    assert all(cfg.enabled.values())
    assert cfg.durations_ms == DEFAULT_DURATIONS
    assert list(cfg.durations_ms) == list(REGISTRY)
    assert cfg.frequency_s == 60
    assert cfg.hotkey == "home"


def test_config_path_is_in_app_dir() -> None:
    assert config.config_path() == paths.app_dir() / "chaos_config.json"


def test_missing_file_gives_defaults_without_warning(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG)
    cfg = config.load(tmp_path / "absent.json")
    assert cfg == Config()
    assert warnings_of(caplog) == []


def test_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "chaos_config.json"
    cfg = Config()
    cfg.frequency_s = 42
    cfg.enabled["flashbang"] = False
    cfg.enabled["mosquito"] = False
    cfg.durations_ms["tunnel_vision"] = 500
    cfg.durations_ms["mosquito"] = 60000
    assert config.save(cfg, path) is True
    assert config.load(path) == cfg


def test_saved_file_is_utf8_indent_2(tmp_path: Path) -> None:
    path = tmp_path / "chaos_config.json"
    assert config.save(Config(), path)
    text = path.read_text(encoding="utf-8")
    assert text.startswith('{\n  "frequency_s": 60,\n')
    assert json.loads(text)["hotkey"] == "home"


def test_corrupt_json_gives_defaults_and_warning(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    path = tmp_path / "chaos_config.json"
    path.write_text('{"frequency_s": 30,', encoding="utf-8")
    assert config.load(path) == Config()
    assert len(warnings_of(caplog)) == 1


def test_invalid_utf8_gives_defaults_and_warning(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    path = tmp_path / "chaos_config.json"
    path.write_bytes(b'{"frequency_s": "\xff\xfe"}')
    assert config.load(path) == Config()
    assert len(warnings_of(caplog)) == 1


@pytest.mark.parametrize("data", [[1, 2], "texte", 12, None])
def test_top_level_not_an_object(tmp_path: Path, caplog: pytest.LogCaptureFixture, data: Any) -> None:
    path = write_json(tmp_path / "c.json", data)
    assert config.load(path) == Config()
    assert len(warnings_of(caplog)) == 1


def test_wrong_types_fall_back_field_by_field(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    path = write_json(
        tmp_path / "c.json",
        {
            "frequency_s": "30",
            "enabled": {"flashbang": "non", "tunnel_vision": False},
            "durations_ms": {"flashbang": "2500", "scanlines": 1500.5, "mosquito": 1234},
            "hotkey": 5,
        },
    )
    cfg = config.load(path)
    assert cfg.frequency_s == 60
    assert cfg.enabled["flashbang"] is True
    assert cfg.enabled["tunnel_vision"] is False
    assert cfg.durations_ms["flashbang"] == DEFAULT_DURATIONS["flashbang"]
    assert cfg.durations_ms["scanlines"] == DEFAULT_DURATIONS["scanlines"]
    assert cfg.durations_ms["mosquito"] == 1234
    assert cfg.hotkey == "home"
    assert len(warnings_of(caplog)) == 5


def test_booleans_are_not_numbers(tmp_path: Path) -> None:
    path = write_json(tmp_path / "c.json", {"frequency_s": True, "durations_ms": {"flashbang": True}})
    cfg = config.load(path)
    assert cfg.frequency_s == 60
    assert cfg.durations_ms["flashbang"] == DEFAULT_DURATIONS["flashbang"]


def test_sections_not_objects(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    path = write_json(tmp_path / "c.json", {"enabled": [True], "durations_ms": 3000, "frequency_s": 10})
    cfg = config.load(path)
    assert cfg.frequency_s == 10
    assert cfg.enabled == Config().enabled
    assert cfg.durations_ms == DEFAULT_DURATIONS
    assert len(warnings_of(caplog)) == 2


@pytest.mark.parametrize(("value", "expected"), [(0, 60), (-5, 60), (3601, 60), (1, 1), (3600, 3600), (90, 90)])
def test_frequency_bounds(tmp_path: Path, value: int, expected: int) -> None:
    path = write_json(tmp_path / "c.json", {"frequency_s": value})
    assert config.load(path).frequency_s == expected


@pytest.mark.parametrize(("value", "valid"), [(499, False), (500, True), (60000, True), (60001, False), (-1, False)])
def test_duration_bounds(tmp_path: Path, caplog: pytest.LogCaptureFixture, value: int, valid: bool) -> None:
    path = write_json(tmp_path / "c.json", {"durations_ms": {"paranoia": value}})
    cfg = config.load(path)
    assert cfg.durations_ms["paranoia"] == (value if valid else DEFAULT_DURATIONS["paranoia"])
    assert len(warnings_of(caplog)) == (0 if valid else 1)


def test_unknown_keys_are_ignored(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    path = write_json(
        tmp_path / "c.json",
        {"frequency_s": 15, "volume": 3, "enabled": {"nouveau_malus": True}, "durations_ms": {"x": 9}},
    )
    cfg = config.load(path)
    assert cfg.frequency_s == 15
    assert "nouveau_malus" not in cfg.enabled
    assert "x" not in cfg.durations_ms
    assert "volume" not in cfg.to_dict()
    assert warnings_of(caplog) == []


def test_missing_malus_keys_are_filled(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    path = write_json(tmp_path / "c.json", {"enabled": {"flashbang": False}, "durations_ms": {"flashbang": 700}})
    cfg = config.load(path)
    assert list(cfg.enabled) == list(REGISTRY)
    assert list(cfg.durations_ms) == list(REGISTRY)
    assert cfg.enabled["flashbang"] is False
    assert all(cfg.enabled[key] for key in REGISTRY if key != "flashbang")
    assert cfg.durations_ms["flashbang"] == 700
    assert cfg.durations_ms["mosquito"] == DEFAULT_DURATIONS["mosquito"]
    assert warnings_of(caplog) == []


@pytest.mark.parametrize(("value", "warns"), [("home", False), ("HOME", False), ("end", True), ("", True)])
def test_hotkey_only_home(tmp_path: Path, caplog: pytest.LogCaptureFixture, value: str, warns: bool) -> None:
    path = write_json(tmp_path / "c.json", {"hotkey": value})
    assert config.load(path).hotkey == "home"
    assert len(warnings_of(caplog)) == (1 if warns else 0)


def test_atomic_save_leaves_no_temp_file(tmp_path: Path) -> None:
    path = tmp_path / "chaos_config.json"
    assert config.save(Config(), path)
    cfg = Config()
    cfg.frequency_s = 5
    assert config.save(cfg, path)  # remplace un fichier existant
    assert sorted(p.name for p in tmp_path.iterdir()) == ["chaos_config.json"]
    assert config.load(path).frequency_s == 5


def test_save_failure_returns_false(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    path = tmp_path / "dossier_absent" / "chaos_config.json"
    assert config.save(Config(), path) is False
    assert len(warnings_of(caplog)) == 1
    assert not path.exists()


def test_replace_failure_keeps_old_file_and_removes_temp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "chaos_config.json"
    assert config.save(Config(), path)
    before = path.read_text(encoding="utf-8")

    def broken_replace(src: str, dst: object) -> None:
        raise PermissionError("fichier verrouillé")

    monkeypatch.setattr(os, "replace", broken_replace)
    cfg = Config()
    cfg.frequency_s = 7
    assert config.save(cfg, path) is False
    assert path.read_text(encoding="utf-8") == before
    assert sorted(p.name for p in tmp_path.iterdir()) == ["chaos_config.json"]


def test_clamp_frequency() -> None:
    assert config.clamp_frequency(0) == 1
    assert config.clamp_frequency(99999) == 3600
    assert config.clamp_frequency(45) == 45


def test_custom_malus_defaults(tmp_path: Path) -> None:
    cfg = config.load(tmp_path / "absent.json", {"a": 1000, "b": 2000})
    assert cfg.enabled == {"a": True, "b": True}
    assert cfg.durations_ms == {"a": 1000, "b": 2000}


def test_import_config_without_qt() -> None:
    code = (
        "import sys\n"
        "import chaos_overlay.config\n"
        "assert 'PySide6' not in sys.modules, 'Qt importe'\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, result.stderr


def test_defaults_profile_and_screen() -> None:
    cfg = Config()
    assert (cfg.profile, cfg.screen) == ("generic", 0)


def test_v2_file_without_profile_or_screen_still_loads(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Un chaos_config.json écrit par la v2 reste valide : les nouveaux champs prennent leur défaut."""
    path = write_json(tmp_path / "c.json", {"frequency_s": 30, "enabled": {"flashbang": False}, "hotkey": "home"})
    cfg = config.load(path)
    assert (cfg.frequency_s, cfg.enabled["flashbang"], cfg.profile, cfg.screen) == (30, False, "generic", 0)
    assert warnings_of(caplog) == []


@pytest.mark.parametrize("profile", ["valorant", "cs2", "apex", "overwatch2", "generic"])
def test_known_profiles_are_kept(tmp_path: Path, profile: str) -> None:
    assert config.load(write_json(tmp_path / "c.json", {"profile": profile})).profile == profile


@pytest.mark.parametrize("value", ["fortnite", 3, None, ""])
def test_unknown_profile_falls_back(tmp_path: Path, caplog: pytest.LogCaptureFixture, value: Any) -> None:
    assert config.load(write_json(tmp_path / "c.json", {"profile": value})).profile == "generic"
    assert len(warnings_of(caplog)) == 1


@pytest.mark.parametrize(("value", "expected"), [(0, 0), (2, 2), (15, 15), (-1, 0), (16, 0), (True, 0), ("1", 0)])
def test_screen_bounds(tmp_path: Path, value: Any, expected: int) -> None:
    assert config.load(write_json(tmp_path / "c.json", {"screen": value})).screen == expected


def test_clamp_duration() -> None:
    assert config.clamp_duration(10) == 500
    assert config.clamp_duration(99999) == 60000
    assert config.clamp_duration(1234) == 1234
