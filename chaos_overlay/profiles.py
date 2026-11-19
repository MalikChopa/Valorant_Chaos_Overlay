"""Profils de jeu : ce qui change d'un FPS à l'autre (pour l'instant, les zones du HUD).

Module pur : aucun import Qt. Un profil ne détecte pas le jeu et ne lit rien dans le jeu :
c'est le streamer qui le choisit dans le Dashboard. Les zones sont des approximations,
exprimées en fractions de l'écran (0 = bord gauche/haut, 1 = bord droit/bas), donc
valables quelle que soit la résolution.
"""

from __future__ import annotations

from dataclasses import dataclass

# (x0, y0, x1, y1) en fractions de la largeur et de la hauteur de l'écran.
Zone = tuple[float, float, float, float]


@dataclass(frozen=True)
class GameProfile:
    """Un jeu (ou « générique ») : nom affiché et zones du HUD masquées par `hud_blocker`."""

    key: str
    name: str
    hud_zones: tuple[Zone, ...]


DEFAULT_PROFILE = "generic"

# Ordre d'affichage dans le Dashboard.
PROFILES: dict[str, GameProfile] = {
    profile.key: profile
    for profile in (
        GameProfile(
            key="generic",
            name="Générique (tous les FPS)",
            hud_zones=((0.0, 0.0, 0.20, 0.30), (0.0, 0.85, 0.25, 1.0), (0.75, 0.85, 1.0, 1.0)),
        ),
        GameProfile(
            key="valorant",
            name="Valorant",
            # Les zones de la v2 : minimap, bas droite, bas entre 25 % et 45 % de la largeur.
            hud_zones=((0.0, 0.0, 0.20, 0.30), (0.75, 0.80, 1.0, 1.0), (0.25, 0.85, 0.45, 1.0)),
        ),
        GameProfile(
            key="cs2",
            name="Counter-Strike 2",
            hud_zones=((0.0, 0.0, 0.18, 0.30), (0.0, 0.90, 0.30, 1.0), (0.80, 0.90, 1.0, 1.0)),
        ),
        GameProfile(
            key="apex",
            name="Apex Legends",
            hud_zones=((0.0, 0.0, 0.17, 0.28), (0.0, 0.80, 0.30, 1.0), (0.72, 0.82, 1.0, 1.0)),
        ),
        GameProfile(
            key="overwatch2",
            name="Overwatch 2",
            hud_zones=((0.38, 0.0, 0.62, 0.13), (0.0, 0.82, 0.30, 1.0), (0.65, 0.85, 1.0, 1.0)),
        ),
    )
}


def get_profile(key: str) -> GameProfile:
    """Profil de clé `key` ; le profil générique si la clé est inconnue."""
    return PROFILES.get(key, PROFILES[DEFAULT_PROFILE])
