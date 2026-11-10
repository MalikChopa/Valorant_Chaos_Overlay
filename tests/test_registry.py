"""Tests du registre des malus et des imports sans effet de bord."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from chaos_overlay.malus import REGISTRY, Malus, register

PROJECT_ROOT = Path(__file__).resolve().parent.parent

EXPECTED = [
    ("flashbang", 2500),
    ("tunnel_vision", 8000),
    ("hud_blocker", 12000),
    ("fake_crosshair", 10000),
    ("scanlines", 10000),
    ("mlg_fullscreen", 6000),
    ("fake_crash", 2500),
    ("blind_spot", 8000),
    ("paranoia", 4000),
    ("screen_crack", 8000),
    ("mosquito", 10000),
]


def test_registry_keys_in_display_order() -> None:
    assert list(REGISTRY) == [key for key, _ in EXPECTED]


def test_registry_durations() -> None:
    assert [(key, cls.default_duration_ms) for key, cls in REGISTRY.items()] == EXPECTED


def test_registry_classes_are_malus_with_matching_key() -> None:
    for key, malus_class in REGISTRY.items():
        assert issubclass(malus_class, Malus)
        assert malus_class.key == key


def test_register_refuses_duplicate_key() -> None:
    class Duplicate(Malus):
        key = "flashbang"
        default_duration_ms = 1

        def _draw(self, ctx: object) -> None:  # type: ignore[override]
            pass

    with pytest.raises(ValueError):
        register(Duplicate)
    assert REGISTRY["flashbang"] is not Duplicate


def run_python(code: str) -> subprocess.CompletedProcess[str]:
    """Lance un interpréteur neuf depuis la racine du projet (aucun état partagé avec pytest)."""
    return subprocess.run(
        [sys.executable, "-c", code], cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=60
    )


def test_import_malus_and_scheduler_has_no_side_effect() -> None:
    code = (
        "import os, sys, tkinter\n"
        "cwd, out, err = os.getcwd(), sys.stdout, sys.stderr\n"
        "import chaos_overlay.malus, chaos_overlay.scheduler\n"
        "assert tkinter._default_root is None, 'une fenetre Tk a ete creee'\n"
        "assert os.getcwd() == cwd, 'chdir a l import'\n"
        "assert sys.stdout is out and sys.stderr is err, 'stdout remplace a l import'\n"
        "assert len(chaos_overlay.malus.REGISTRY) == 11\n"
        "print('OK')\n"
    )
    result = run_python(code)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "OK"


def test_scheduler_does_not_import_tkinter() -> None:
    result = run_python("import sys, chaos_overlay.scheduler; print('tkinter' in sys.modules)")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "False"


def test_import_ui_and_app_opens_no_window() -> None:
    code = (
        "import os, sys, tkinter\n"
        "cwd = os.getcwd()\n"
        "import chaos_overlay.ui.dashboard, chaos_overlay.ui.overlay, chaos_overlay.ui.splash\n"
        "import chaos_overlay.ui.roulette, chaos_overlay.app\n"
        "assert tkinter._default_root is None, 'une fenetre Tk a ete creee'\n"
        "assert os.getcwd() == cwd\n"
        "print('OK')\n"
    )
    result = run_python(code)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "OK"
