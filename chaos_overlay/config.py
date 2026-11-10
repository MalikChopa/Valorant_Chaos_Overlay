"""Réglages enregistrés dans chaos_config.json (à côté de l'exe, ou à la racine du projet).

Module pur : aucun import de tkinter au chargement, aucune fenêtre.
Un fichier absent donne les valeurs par défaut ; un fichier abîmé aussi, avec un avertissement
dans le journal, mais jamais de plantage.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from chaos_overlay.paths import app_dir

logger = logging.getLogger(__name__)

CONFIG_NAME = "chaos_config.json"

DEFAULT_FREQUENCY_S = 60
MIN_FREQUENCY_S = 1
MAX_FREQUENCY_S = 3600
MIN_DURATION_MS = 500
MAX_DURATION_MS = 60000
DEFAULT_HOTKEY = "home"
SUPPORTED_HOTKEYS = ("home",)


def default_malus_durations() -> dict[str, int]:
    """Durée par défaut de chaque malus, dans l'ordre du registre (import tardif du registre)."""
    from chaos_overlay.malus import REGISTRY

    return {key: malus_class.default_duration_ms for key, malus_class in REGISTRY.items()}


def _default_enabled() -> dict[str, bool]:
    return {key: True for key in default_malus_durations()}


@dataclass
class Config:
    """Réglages du chaos : fréquence, malus cochés, durées, touche du Dashboard."""

    frequency_s: int = DEFAULT_FREQUENCY_S
    enabled: dict[str, bool] = field(default_factory=_default_enabled)
    durations_ms: dict[str, int] = field(default_factory=default_malus_durations)
    hotkey: str = DEFAULT_HOTKEY

    def to_dict(self) -> dict[str, Any]:
        """Version JSON des réglages."""
        return {
            "frequency_s": self.frequency_s,
            "enabled": dict(self.enabled),
            "durations_ms": dict(self.durations_ms),
            "hotkey": self.hotkey,
        }


def config_path() -> Path:
    """Chemin du fichier de réglages : app_dir() / chaos_config.json."""
    return app_dir() / CONFIG_NAME


def clamp_frequency(seconds: int) -> int:
    """Ramène une fréquence dans les bornes 1..3600 s."""
    return max(MIN_FREQUENCY_S, min(MAX_FREQUENCY_S, seconds))


def _is_int(value: object) -> bool:
    """Vrai pour un entier JSON (True/False ne comptent pas comme des entiers)."""
    return isinstance(value, int) and not isinstance(value, bool)


def _read_frequency(raw: Mapping[str, Any]) -> int:
    if "frequency_s" not in raw:
        return DEFAULT_FREQUENCY_S
    value = raw["frequency_s"]
    if _is_int(value) and MIN_FREQUENCY_S <= value <= MAX_FREQUENCY_S:
        return int(value)
    logger.warning(
        "Config : frequency_s=%r invalide (entier de %d à %d attendu), valeur par défaut %d utilisée",
        value,
        MIN_FREQUENCY_S,
        MAX_FREQUENCY_S,
        DEFAULT_FREQUENCY_S,
    )
    return DEFAULT_FREQUENCY_S


def _read_section(raw: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    """Renvoie la sous-table `name` (vide si absente ; avertissement si ce n'est pas un objet)."""
    if name not in raw:
        return {}
    section = raw[name]
    if isinstance(section, dict):
        return section
    logger.warning("Config : %s doit être un objet JSON, valeurs par défaut utilisées", name)
    return {}


def _read_enabled(raw: Mapping[str, Any], keys: list[str]) -> dict[str, bool]:
    section = _read_section(raw, "enabled")
    enabled: dict[str, bool] = {}
    for key in keys:
        value = section.get(key, True)
        if isinstance(value, bool):
            enabled[key] = value
        else:
            logger.warning("Config : enabled.%s=%r invalide (true/false attendu), malus activé", key, value)
            enabled[key] = True
    return enabled


def _read_durations(raw: Mapping[str, Any], defaults: Mapping[str, int]) -> dict[str, int]:
    section = _read_section(raw, "durations_ms")
    durations: dict[str, int] = {}
    for key, default in defaults.items():
        value = section.get(key, default)
        if _is_int(value) and MIN_DURATION_MS <= value <= MAX_DURATION_MS:
            durations[key] = int(value)
        else:
            logger.warning(
                "Config : durations_ms.%s=%r invalide (entier de %d à %d attendu), durée par défaut %d ms",
                key,
                value,
                MIN_DURATION_MS,
                MAX_DURATION_MS,
                default,
            )
            durations[key] = default
    return durations


def _read_hotkey(raw: Mapping[str, Any]) -> str:
    value = raw.get("hotkey", DEFAULT_HOTKEY)
    if isinstance(value, str) and value.strip().lower() in SUPPORTED_HOTKEYS:
        return value.strip().lower()
    logger.warning("Config : hotkey=%r non prise en charge (seulement \"home\"), HOME utilisée", value)
    return DEFAULT_HOTKEY


def from_dict(raw: Mapping[str, Any], malus_defaults: Mapping[str, int] | None = None) -> Config:
    """Construit une Config valide champ par champ ; un champ invalide reprend sa valeur par défaut."""
    defaults = dict(malus_defaults) if malus_defaults is not None else default_malus_durations()
    return Config(
        frequency_s=_read_frequency(raw),
        enabled=_read_enabled(raw, list(defaults)),
        durations_ms=_read_durations(raw, defaults),
        hotkey=_read_hotkey(raw),
    )


def load(path: Path, malus_defaults: Mapping[str, int] | None = None) -> Config:
    """Lit le fichier de réglages. Ne plante jamais : en cas de souci, valeurs par défaut."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return from_dict({}, malus_defaults)
    except (OSError, UnicodeDecodeError):
        logger.warning("Config : lecture de %s impossible, valeurs par défaut utilisées", path, exc_info=True)
        return from_dict({}, malus_defaults)

    try:
        raw = json.loads(text)
    except json.JSONDecodeError as error:
        logger.warning("Config : %s n'est pas un JSON valide (%s), valeurs par défaut utilisées", path, error)
        return from_dict({}, malus_defaults)

    if not isinstance(raw, dict):
        logger.warning("Config : %s doit contenir un objet JSON, valeurs par défaut utilisées", path)
        return from_dict({}, malus_defaults)
    return from_dict(raw, malus_defaults)


def save(config: Config, path: Path) -> bool:
    """Écrit les réglages (UTF-8, indentation 2) sans risquer un fichier à moitié écrit.

    On écrit d'abord un fichier temporaire dans le même dossier, puis os.replace le met à la place.
    Renvoie False (et journalise) si l'écriture échoue.
    """
    text = json.dumps(config.to_dict(), indent=2, ensure_ascii=False) + "\n"
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False
        ) as temp_file:
            temp_name = temp_file.name
            temp_file.write(text)
            temp_file.flush()
            os.fsync(temp_file.fileno())
        os.replace(temp_name, path)
    except OSError:
        logger.warning("Config : impossible d'enregistrer %s", path, exc_info=True)
        if temp_name is not None:
            try:
                os.remove(temp_name)
            except OSError:
                pass
        return False
    return True
