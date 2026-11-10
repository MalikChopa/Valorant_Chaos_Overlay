"""Tests de chaos_overlay.logs : fichier tournant, console facultative, jamais de plantage."""

from __future__ import annotations

import logging
import sys
from collections.abc import Iterator
from logging.handlers import RotatingFileHandler
from pathlib import Path

import pytest

from chaos_overlay import logs, paths


@pytest.fixture
def target() -> Iterator[logging.Logger]:
    """Logger dédié au test (le logger racine n'est pas touché), nettoyé à la fin."""
    logger = logging.getLogger("test_logs_cible")
    logger.propagate = False
    yield logger
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()


def file_handlers(logger: logging.Logger) -> list[RotatingFileHandler]:
    return [h for h in logger.handlers if isinstance(h, RotatingFileHandler)]


def test_log_path_is_in_app_dir() -> None:
    assert logs.log_path() == paths.app_dir() / "chaos_overlay.log"


def test_file_handler_in_tmp_path(tmp_path: Path, target: logging.Logger) -> None:
    log_file = tmp_path / "chaos_overlay.log"
    logs.setup_logging(log_file, target=target)
    (handler,) = file_handlers(target)
    assert handler.maxBytes == 256 * 1024
    assert handler.backupCount == 2
    assert handler.encoding == "utf-8"

    target.warning("mlg.gif introuvable, élément ignoré")
    handler.flush()
    text = log_file.read_text(encoding="utf-8")
    assert "WARNING" in text and "élément ignoré" in text


def test_unwritable_path_does_not_crash(tmp_path: Path, target: logging.Logger) -> None:
    bad_path = tmp_path / "dossier_absent" / "chaos_overlay.log"
    added = logs.setup_logging(bad_path, target=target)
    assert file_handlers(target) == []
    assert not bad_path.exists()
    assert all(isinstance(h, logging.StreamHandler) for h in added)


def test_console_only_when_stderr_exists(
    tmp_path: Path, target: logging.Logger, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "stderr", None)
    added = logs.setup_logging(tmp_path / "a.log", target=target)
    assert [type(h) for h in added] == [RotatingFileHandler]


def test_console_added_when_stderr_exists(tmp_path: Path, target: logging.Logger) -> None:
    added = logs.setup_logging(tmp_path / "a.log", target=target)
    assert sorted(type(h).__name__ for h in added) == ["RotatingFileHandler", "StreamHandler"]


def test_no_stderr_and_no_file_still_no_crash(
    tmp_path: Path, target: logging.Logger, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "stderr", None)
    assert logs.setup_logging(tmp_path / "absent" / "a.log", target=target) == []


def test_called_twice_does_not_duplicate_handlers(tmp_path: Path, target: logging.Logger) -> None:
    foreign = logging.NullHandler()
    target.addHandler(foreign)
    logs.setup_logging(tmp_path / "a.log", target=target)
    logs.setup_logging(tmp_path / "a.log", target=target)
    assert len(file_handlers(target)) == 1
    assert foreign in target.handlers  # un handler qui n'est pas à nous reste en place
    assert target.level == logging.INFO
