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
from chaos_overlay.malus import sniper_scope
from chaos_overlay.malus import low_hp
from chaos_overlay.malus import fake_kill_feed
from chaos_overlay.malus import drunk_crosshair
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
    "sniper_scope",
    "low_hp",
    "fake_kill_feed",
    "drunk_crosshair",
]


def label_of(key: str) -> str:
    """Nom affiché d'un malus (ou de « rien » quand aucun malus n'est coché)."""
    malus_class = REGISTRY.get(key)
    return malus_class.label if malus_class is not None else key.replace("_", " ").capitalize()
