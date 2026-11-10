"""Tests de chaos_overlay.hotkey avec un faux user32 : aucun vrai raccourci système n'est enregistré."""

from __future__ import annotations

import queue
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from chaos_overlay import app, hotkey
from chaos_overlay.hotkey import HOTKEY_ID, MOD_NOREPEAT, VK_HOME, WM_HOTKEY, WM_QUIT, HomeHotkey

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class FakeUser32:
    """Imite les 4 fonctions user32 utilisées ; GetMessageW lit une file Python."""

    def __init__(self, register_result: int = 1, get_message_error: bool = False) -> None:
        self.register_result = register_result
        self.get_message_error = get_message_error
        self.messages: queue.Queue[tuple[int, int]] = queue.Queue()
        self.registered: list[tuple[Any, ...]] = []
        self.unregistered: list[tuple[Any, ...]] = []
        self.posted: list[tuple[Any, ...]] = []

    def RegisterHotKey(self, hwnd: Any, hotkey_id: int, modifiers: int, vk: int) -> int:  # noqa: N802
        self.registered.append((hwnd, hotkey_id, modifiers, vk))
        return self.register_result

    def UnregisterHotKey(self, hwnd: Any, hotkey_id: int) -> int:  # noqa: N802
        self.unregistered.append((hwnd, hotkey_id))
        return 1

    def GetMessageW(self, msg_pointer: Any, hwnd: Any, low: int, high: int) -> int:  # noqa: N802
        if self.get_message_error:
            return -1
        message, wparam = self.messages.get(timeout=5)
        msg_pointer.contents.message = message
        msg_pointer.contents.wParam = wparam
        return 0 if message == WM_QUIT else 1

    def PostThreadMessageW(self, thread_id: int, message: int, wparam: int, lparam: int) -> int:  # noqa: N802
        self.posted.append((thread_id, message, wparam, lparam))
        self.messages.put((message, wparam))
        return 1


class FakeAfter:
    """Faux root.after : retient les appels programmés, on les lance à la main."""

    def __init__(self) -> None:
        self.scheduled: list[tuple[int, Callable[[], None]]] = []

    def __call__(self, delay_ms: int, callback: Callable[[], None]) -> str:
        self.scheduled.append((delay_ms, callback))
        return f"after#{len(self.scheduled)}"

    def run_next(self) -> None:
        _, callback = self.scheduled.pop(0)
        callback()


def wait_for(condition: Callable[[], bool], timeout: float = 5.0) -> bool:
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if condition():
            return True
        time.sleep(0.01)
    return condition()


def make_hotkey(user32: FakeUser32) -> tuple[HomeHotkey, FakeAfter, list[int]]:
    calls: list[int] = []
    after = FakeAfter()
    return HomeHotkey(lambda: calls.append(1), after, user32=user32), after, calls


def test_poll_calls_callback_once_per_token() -> None:
    hk, _, calls = make_hotkey(FakeUser32())
    for _ in range(3):
        hk._tokens.put(1)
    assert hk.poll() == 3
    assert calls == [1, 1, 1]
    assert hk.poll() == 0
    assert calls == [1, 1, 1]


def test_start_returns_false_when_register_fails() -> None:
    user32 = FakeUser32(register_result=0)
    hk, after, _ = make_hotkey(user32)
    assert hk.start() is False
    assert user32.registered == [(None, HOTKEY_ID, MOD_NOREPEAT, VK_HOME)]
    assert after.scheduled == []  # pas de scrutation si l'enregistrement a échoué
    assert hk._thread is not None and wait_for(lambda: not hk._thread.is_alive())  # type: ignore[union-attr]
    assert user32.unregistered == []
    hk.stop()  # sans effet, sans erreur


def test_start_returns_false_without_user32(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(hotkey, "_load_user32", lambda: None)
    hk = HomeHotkey(lambda: None, FakeAfter())
    assert hk.start() is False


def test_full_cycle_with_fake_user32() -> None:
    user32 = FakeUser32()
    hk, after, calls = make_hotkey(user32)
    assert hk.start() is True
    assert hk.is_active
    assert user32.registered == [(None, HOTKEY_ID, MOD_NOREPEAT, VK_HOME)]
    assert [delay for delay, _ in after.scheduled] == [100]

    # Deux appuis sur HOME, plus un message d'un autre raccourci qui doit être ignoré.
    user32.messages.put((WM_HOTKEY, HOTKEY_ID))
    user32.messages.put((WM_HOTKEY, 99))
    user32.messages.put((WM_HOTKEY, HOTKEY_ID))
    assert wait_for(lambda: hk._tokens.qsize() == 2)
    assert calls == []  # rien n'est appelé depuis le thread de travail

    after.run_next()  # la scrutation Tk vide la file et se reprogramme
    assert calls == [1, 1]
    assert [delay for delay, _ in after.scheduled] == [100]

    hk.stop()
    assert [m for _, m, _, _ in user32.posted] == [WM_QUIT]
    assert hk._thread is not None and not hk._thread.is_alive()
    assert user32.unregistered == [(None, HOTKEY_ID)]
    assert not hk.is_active

    after.run_next()  # après stop(), la scrutation ne se reprogramme plus
    assert after.scheduled == []


def test_start_twice_registers_once() -> None:
    user32 = FakeUser32()
    hk, _, _ = make_hotkey(user32)
    assert hk.start() and hk.start()
    assert len(user32.registered) == 1
    hk.stop()


def test_get_message_error_stops_thread_and_unregisters() -> None:
    user32 = FakeUser32(get_message_error=True)
    hk, _, _ = make_hotkey(user32)
    hk.start()
    assert hk._thread is not None and wait_for(lambda: not hk._thread.is_alive())  # type: ignore[union-attr]
    assert user32.unregistered == [(None, HOTKEY_ID)]
    hk.stop()


def test_poll_loop_keeps_running_if_callback_fails() -> None:
    after = FakeAfter()

    def boom() -> None:
        raise RuntimeError("callback en erreur")

    hk = HomeHotkey(boom, after, user32=FakeUser32())
    hk._polling = True
    hk._tokens.put(1)
    with pytest.raises(RuntimeError):
        hk._poll_loop()
    assert len(after.scheduled) == 1


@pytest.mark.skipif(sys.platform != "win32", reason="user32.dll n'existe que sous Windows")
def test_real_user32_loader_sets_signatures_only() -> None:
    user32 = hotkey._load_user32()
    assert user32 is not None
    assert len(user32.RegisterHotKey.argtypes) == 4
    assert len(user32.GetMessageW.argtypes) == 4
    assert len(user32.PostThreadMessageW.argtypes) == 4


def test_warning_text_no_longer_mentions_admin() -> None:
    assert "Administrateur" not in app.HOTKEY_WARNING
    assert "HOME" in app.HOTKEY_WARNING


def test_imports_without_window_and_without_keyboard_lib() -> None:
    code = (
        "import sys, tkinter\n"
        "import chaos_overlay.app, chaos_overlay.hotkey, chaos_overlay.config, chaos_overlay.logs\n"
        "assert tkinter._default_root is None, 'racine Tk creee'\n"
        "assert 'keyboard' not in sys.modules, 'lib keyboard importee'\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, result.stderr
