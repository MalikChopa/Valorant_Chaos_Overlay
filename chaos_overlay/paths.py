"""Chemins de l'application, sans jamais changer le dossier courant (pas de chdir)."""

from __future__ import annotations

import sys
from pathlib import Path

# Racine du projet : le dossier qui contient le paquet chaos_overlay.
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def app_dir() -> Path:
    """Dossier de l'exe (version PyInstaller) ou racine du projet (version script).

    C'est là qu'on écrit les fichiers visibles par l'utilisateur (crash_log.txt).
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return PROJECT_ROOT


def resource_path(filename: str) -> Path:
    """Chemin d'une ressource embarquée (dossier _MEIPASS de PyInstaller, sinon le projet)."""
    bundle_dir = getattr(sys, "_MEIPASS", None)
    if bundle_dir:
        return Path(str(bundle_dir)) / filename
    return PROJECT_ROOT / filename
