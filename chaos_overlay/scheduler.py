"""Logique pure du tirage et de la roulette (aucun import tkinter)."""

from __future__ import annotations

import random
from collections.abc import Sequence

# Valeur tirée quand aucun malus n'est coché (comme dans le code d'origine).
NOTHING = "rien"

ROULETTE_SPINS = 30
ROULETTE_START_DELAY_MS = 50
ROULETTE_RESULT_PAUSE_MS = 1500


def roulette_pool(active: Sequence[str]) -> list[str]:
    """Noms affichés par la roulette : les malus actifs, ou ["rien"] si la liste est vide."""
    if active:
        return list(active)
    return [NOTHING]


def pick(active: Sequence[str], rng: random.Random) -> str:
    """Tire le malus final parmi les malus actifs ("rien" si aucun)."""
    return rng.choice(roulette_pool(active))


def roulette_delays(spins: int = ROULETTE_SPINS, start_delay: int = ROULETTE_START_DELAY_MS) -> list[int]:
    """Délais (ms) entre deux noms de la roulette : elle ralentit à chaque tour.

    Même formule que le code d'origine : new_delay = delay + int(120 / spins_left).
    """
    delays: list[int] = []
    delay = start_delay
    for spins_left in range(spins, 0, -1):
        delay = delay + int(120 / spins_left)
        delays.append(delay)
    return delays


def parse_frequency(text: str) -> int | None:
    """Fréquence saisie (secondes) : entier >= 1 en chiffres ASCII, sinon None."""
    if not (text.isascii() and text.isdigit()):
        return None
    value = int(text)
    if value < 1:
        return None
    return value


def display_name(key: str) -> str:
    """Nom affiché d'un malus : "tunnel_vision" -> "TUNNEL VISION"."""
    return key.replace("_", " ").upper()
