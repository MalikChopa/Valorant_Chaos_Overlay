"""Journal de l'application : console (si elle existe) + fichier chaos_overlay.log à côté de l'exe.

Pourquoi un fichier : l'exe fenêtré n'a pas de console, les avertissements y étaient invisibles.
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from chaos_overlay.paths import app_dir

LOG_NAME = "chaos_overlay.log"
MAX_BYTES = 256 * 1024
BACKUP_COUNT = 2
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"

# Marque posée sur nos handlers, pour ne pas les ajouter deux fois si setup_logging est rappelé.
_OWNED = "_chaos_overlay_handler"


def log_path() -> Path:
    """Chemin du fichier journal : app_dir() / chaos_overlay.log."""
    return app_dir() / LOG_NAME


def setup_logging(
    path: Path | None = None,
    level: int = logging.INFO,
    target: logging.Logger | None = None,
) -> list[logging.Handler]:
    """Branche la console (si stderr existe) et le fichier tournant (256 Ko, 2 sauvegardes).

    Ne plante jamais : si le fichier ne peut pas être ouvert, on garde la console seule.
    `target` sert aux tests (par défaut : le logger racine). Renvoie les handlers ajoutés.
    """
    logger = target if target is not None else logging.getLogger()
    for handler in list(logger.handlers):
        if getattr(handler, _OWNED, False):
            logger.removeHandler(handler)
            handler.close()

    logger.setLevel(level)
    formatter = logging.Formatter(LOG_FORMAT)
    added: list[logging.Handler] = []

    if sys.stderr is not None:
        console = logging.StreamHandler(sys.stderr)
        added.append(console)

    file_path = path if path is not None else log_path()
    file_error: OSError | None = None
    try:
        added.append(RotatingFileHandler(file_path, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"))
    except OSError as error:
        file_error = error

    for handler in added:
        handler.setFormatter(formatter)
        setattr(handler, _OWNED, True)
        logger.addHandler(handler)

    if file_error is not None:
        logger.warning("Journal fichier indisponible (%s) : %s", file_path, file_error)
    return added
