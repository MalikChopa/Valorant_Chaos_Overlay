"""Tous les malus. Importer ce paquet remplit REGISTRY (clé -> classe).

L'ordre des imports ci-dessous est l'ordre d'affichage dans le Dashboard : ne pas le trier.
"""

from __future__ import annotations

from chaos_overlay.malus.base import REGISTRY, EffectContext, Malus, register

# isort: off
from chaos_overlay.malus import flashbang
from chaos_overlay.malus import tunnel_vision
from chaos_overlay.malus import hud_blocker
from chaos_overlay.malus import fake_crosshair
from chaos_overlay.malus import scanlines
from chaos_overlay.malus import mlg_gif
from chaos_overlay.malus import fake_crash
from chaos_overlay.malus import blind_spot
from chaos_overlay.malus import paranoia
from chaos_overlay.malus import screen_crack
from chaos_overlay.malus import mosquito
# isort: on

__all__ = [
    "REGISTRY",
    "EffectContext",
    "Malus",
    "register",
    "flashbang",
    "tunnel_vision",
    "hud_blocker",
    "fake_crosshair",
    "scanlines",
    "mlg_gif",
    "fake_crash",
    "blind_spot",
    "paranoia",
    "screen_crack",
    "mosquito",
]
