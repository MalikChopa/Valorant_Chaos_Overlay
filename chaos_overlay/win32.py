"""Appels Win32 de l'overlay. Seul fichier du projet qui utilise ctypes.windll.

Règle du projet : on ne touche qu'aux styles de NOTRE fenêtre (click-through).
Rien d'autre : pas de lecture d'autres processus, pas d'envoi de touches ni de clics.
"""

from __future__ import annotations

import ctypes
import logging

logger = logging.getLogger(__name__)

GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_NOACTIVATE = 0x08000000
CLICK_THROUGH_STYLES = WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_NOACTIVATE


def toplevel_hwnd(widget_id: int) -> int:
    """Handle Windows de la fenêtre qui contient le widget Tk (0 si introuvable)."""
    windll = getattr(ctypes, "windll", None)
    if windll is None:
        return 0
    try:
        return int(windll.user32.GetParent(widget_id))
    except Exception:  # ctypes.ArgumentError, OSError... : on ne doit jamais planter ici
        logger.warning("GetParent a échoué pour le widget %s", widget_id, exc_info=True)
        return 0


def make_click_through(hwnd: int) -> bool:
    """Rend la fenêtre transparente aux clics. Renvoie True si les styles sont bien posés."""
    windll = getattr(ctypes, "windll", None)
    if windll is None or not hwnd:
        return False
    try:
        user32 = windll.user32
        style = int(user32.GetWindowLongW(hwnd, GWL_EXSTYLE))
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | CLICK_THROUGH_STYLES)
        # On relit le style pour vérifier que Windows l'a bien appliqué.
        new_style = int(user32.GetWindowLongW(hwnd, GWL_EXSTYLE))
    except Exception:  # ctypes.ArgumentError, OSError... : on ne doit jamais planter ici
        logger.warning("Impossible de rendre l'overlay transparent aux clics", exc_info=True)
        return False
    return (new_style & CLICK_THROUGH_STYLES) == CLICK_THROUGH_STYLES
