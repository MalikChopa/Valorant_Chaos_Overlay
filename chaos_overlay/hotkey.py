"""Touche HOME globale, sans droits administrateur, via RegisterHotKey (remplace la lib `keyboard`).

Règle du projet : on enregistre un raccourci auprès de Windows, rien d'autre.
Pas de hook clavier ni souris, pas d'envoi de touches, pas d'accès à un autre processus.

Fonctionnement :
- un thread démon enregistre HOME puis attend ses messages avec GetMessageW ;
- à chaque WM_HOTKEY il dépose un jeton dans une queue.Queue ;
- côté Tk, poll() vide la file toutes les 100 ms (root.after) et appelle le callback
  dans le thread Tk. Le thread de travail ne touche jamais à Tk.
"""

from __future__ import annotations

import ctypes
import logging
import queue
import threading
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)

# Constantes Win32 (winuser.h).
MOD_NOREPEAT = 0x4000
VK_HOME = 0x24
WM_HOTKEY = 0x0312
WM_QUIT = 0x0012

HOTKEY_ID = 1
POLL_INTERVAL_MS = 100
START_TIMEOUT_S = 2.0
STOP_TIMEOUT_S = 1.0

# Planifie un appel dans la boucle Tk : la signature de root.after(ms, fonction).
Scheduler = Callable[[int, Callable[[], None]], object]


def _load_user32() -> Any:
    """Charge user32 avec les signatures des 4 fonctions utilisées (None hors Windows)."""
    win_dll = getattr(ctypes, "WinDLL", None)
    if win_dll is None:
        return None
    from ctypes import wintypes

    try:
        user32 = win_dll("user32", use_last_error=True)
    except OSError:
        logger.warning("user32.dll introuvable", exc_info=True)
        return None
    # Instance WinDLL à nous : ces signatures ne touchent pas ctypes.windll utilisé par win32.py.
    user32.RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.UINT, wintypes.UINT]
    user32.RegisterHotKey.restype = wintypes.BOOL
    user32.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.UnregisterHotKey.restype = wintypes.BOOL
    user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
    user32.GetMessageW.restype = wintypes.BOOL
    user32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user32.PostThreadMessageW.restype = wintypes.BOOL
    return user32


def _new_message() -> Any:
    """Structure MSG vide (wintypes n'est importé qu'ici, à l'exécution)."""
    from ctypes import wintypes

    return wintypes.MSG()


class HomeHotkey:
    """Appelle `callback` (dans le thread Tk) quand on appuie sur HOME, même si le jeu a le focus.

    `after` est root.after. `user32` sert aux tests (faux objet) ; None = le vrai user32.dll.
    """

    def __init__(self, callback: Callable[[], None], after: Scheduler, user32: Any = None) -> None:
        self.callback = callback
        self.after = after
        self._user32 = user32
        self._tokens: queue.Queue[int] = queue.Queue()
        self._thread: threading.Thread | None = None
        self._thread_id: int | None = None
        self._registered = threading.Event()
        self._ready = threading.Event()
        self._polling = False

    @property
    def is_active(self) -> bool:
        """Vrai si le raccourci est enregistré et que le thread tourne."""
        return self._thread is not None and self._thread.is_alive() and self._registered.is_set()

    def start(self) -> bool:
        """Enregistre HOME. Renvoie False si c'est impossible (touche déjà prise, ou pas Windows)."""
        if self.is_active:
            return True
        if self._user32 is None:
            self._user32 = _load_user32()
        if self._user32 is None:
            logger.warning("Raccourci HOME indisponible : RegisterHotKey n'existe que sous Windows")
            return False

        self._registered.clear()
        self._ready.clear()
        self._thread = threading.Thread(target=self._run, name="home-hotkey", daemon=True)
        self._thread.start()
        if not self._ready.wait(START_TIMEOUT_S):
            logger.warning("Raccourci HOME : le thread n'a pas répondu à temps")
            return False
        if not self._registered.is_set():
            return False

        self._polling = True
        self.after(POLL_INTERVAL_MS, self._poll_loop)
        return True

    def stop(self) -> None:
        """Arrête la scrutation, envoie WM_QUIT au thread (qui désenregistre HOME) et l'attend."""
        self._polling = False
        thread = self._thread
        if thread is None or not thread.is_alive():
            return
        if self._thread_id is not None and self._user32 is not None:
            try:
                self._user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
            except Exception:  # ctypes.ArgumentError, OSError... : on ne doit jamais planter ici
                logger.warning("Raccourci HOME : WM_QUIT non envoyé", exc_info=True)
        thread.join(STOP_TIMEOUT_S)
        if thread.is_alive():
            logger.warning("Raccourci HOME : le thread ne s'est pas arrêté (thread démon, il mourra avec l'appli)")

    def poll(self) -> int:
        """Vide la file : un appel du callback par jeton. Renvoie le nombre d'appels (thread Tk)."""
        count = 0
        while True:
            try:
                self._tokens.get_nowait()
            except queue.Empty:
                return count
            count += 1
            self.callback()

    def _poll_loop(self) -> None:
        """Scrutation périodique, reprogrammée par root.after tant que le raccourci est actif."""
        if not self._polling:
            return
        try:
            self.poll()
        finally:
            if self._polling:
                self.after(POLL_INTERVAL_MS, self._poll_loop)

    def _run(self) -> None:
        """Thread de travail : enregistre HOME, attend les messages, désenregistre en sortant."""
        user32 = self._user32
        # Identifiant Windows du thread (même valeur que GetCurrentThreadId), pour PostThreadMessageW.
        self._thread_id = threading.get_native_id()
        try:
            ok = bool(user32.RegisterHotKey(None, HOTKEY_ID, MOD_NOREPEAT, VK_HOME))
        except Exception:  # ctypes.ArgumentError, OSError...
            logger.warning("RegisterHotKey a levé une erreur", exc_info=True)
            ok = False
        if not ok:
            logger.warning("Raccourci HOME refusé par Windows (touche sans doute prise par un autre programme)")
            self._ready.set()
            return

        self._registered.set()
        self._ready.set()
        try:
            self._message_loop(user32)
        finally:
            self._registered.clear()
            try:
                user32.UnregisterHotKey(None, HOTKEY_ID)
            except Exception:
                logger.warning("UnregisterHotKey a levé une erreur", exc_info=True)

    def _message_loop(self, user32: Any) -> None:
        """GetMessageW renvoie 0 sur WM_QUIT, -1 en cas d'erreur : on s'arrête dans les deux cas."""
        msg = _new_message()
        msg_pointer = ctypes.pointer(msg)
        while True:
            result = int(user32.GetMessageW(msg_pointer, None, 0, 0))
            if result == 0:
                return
            if result == -1:
                logger.warning("GetMessageW a échoué : raccourci HOME arrêté")
                return
            if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                self._tokens.put(1)
