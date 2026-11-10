"""Tests des chemins, du journal de crash et du click-through (avec un faux user32)."""

from __future__ import annotations

import ctypes
import sys
from pathlib import Path
from typing import Any

import pytest

from chaos_overlay import app, paths, win32


def test_app_dir_in_dev_is_project_root() -> None:
    assert paths.app_dir() == Path(__file__).resolve().parent.parent
    assert (paths.app_dir() / "chaos_overlay").is_dir()


def test_app_dir_frozen_is_exe_folder(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(tmp_path / "ChaosOverlay.exe"))
    assert paths.app_dir() == tmp_path


def test_resource_path_dev_and_bundle(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    assert paths.resource_path("mlg.gif") == paths.PROJECT_ROOT / "mlg.gif"
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert paths.resource_path("mlg.gif") == tmp_path / "mlg.gif"


def test_crash_log_written_in_app_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(app, "app_dir", lambda: tmp_path)
    try:
        raise RuntimeError("boom de test")
    except RuntimeError:
        app._write_crash_log()
    content = (tmp_path / "crash_log.txt").read_text(encoding="utf-8")
    assert "RuntimeError: boom de test" in content


class FakeUser32:
    """Faux user32 : garde un style par fenêtre ; `refuse=True` simule un SetWindowLongW sans effet."""

    def __init__(self, refuse: bool = False, raise_error: bool = False) -> None:
        self.styles: dict[int, int] = {}
        self.refuse = refuse
        self.raise_error = raise_error

    def GetParent(self, widget_id: int) -> int:  # noqa: N802 (nom Win32)
        return widget_id + 1000

    def GetWindowLongW(self, hwnd: int, index: int) -> int:  # noqa: N802
        if self.raise_error:
            raise OSError("faux échec")
        return self.styles.get(hwnd, 0x100)

    def SetWindowLongW(self, hwnd: int, index: int, value: int) -> int:  # noqa: N802
        previous = self.styles.get(hwnd, 0x100)
        if not self.refuse:
            self.styles[hwnd] = value
        return previous


class FakeWindll:
    def __init__(self, user32: FakeUser32) -> None:
        self.user32 = user32


def install_windll(monkeypatch: pytest.MonkeyPatch, user32: Any) -> None:
    monkeypatch.setattr(ctypes, "windll", FakeWindll(user32), raising=False)


def test_click_through_success(monkeypatch: pytest.MonkeyPatch) -> None:
    user32 = FakeUser32()
    install_windll(monkeypatch, user32)
    hwnd = win32.toplevel_hwnd(5)
    assert hwnd == 1005
    assert win32.make_click_through(hwnd) is True
    assert user32.styles[hwnd] == 0x100 | 0x00080000 | 0x00000020 | 0x08000000


def test_click_through_refused_returns_false(monkeypatch: pytest.MonkeyPatch) -> None:
    install_windll(monkeypatch, FakeUser32(refuse=True))
    assert win32.make_click_through(1005) is False


def test_click_through_error_returns_false(monkeypatch: pytest.MonkeyPatch) -> None:
    install_windll(monkeypatch, FakeUser32(raise_error=True))
    assert win32.make_click_through(1005) is False


def test_click_through_without_hwnd_or_windll(monkeypatch: pytest.MonkeyPatch) -> None:
    assert win32.make_click_through(0) is False
    monkeypatch.delattr(ctypes, "windll", raising=False)
    assert win32.make_click_through(1005) is False
    assert win32.toplevel_hwnd(5) == 0
