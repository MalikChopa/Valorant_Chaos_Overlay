"""MLG : joue mlg.gif au centre de l'écran pendant 6 s (taille d'origine en 1080p).

Le GIF est lu image par image pendant l'effet (QImageReader), sans jamais le charger
en entier : une seule image décodée est gardée en mémoire. Une image toutes les 40 ms ;
on boucle si le GIF est plus court que l'effet.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QImage, QImageReader, QPainter

from chaos_overlay.malus.base import Malus, register
from chaos_overlay.paths import resource_path

GIF_FILENAME = "mlg.gif"
FRAME_DELAY_MS = 40

logger = logging.getLogger(__name__)


class FrameReader(Protocol):
    """Ce qu'on utilise de QImageReader (les tests passent un faux lecteur)."""

    def read(self) -> QImage: ...


def _open_qt_reader(path: Path) -> FrameReader:
    return QImageReader(str(path))


class GifStream:
    """Donne l'image d'indice `index` d'un GIF en le lisant dans l'ordre, sans tout garder.

    Le nombre d'images n'est connu qu'en atteignant la fin du fichier ; ensuite, les indices
    sont pris modulo ce nombre (le GIF boucle).
    """

    def __init__(self, open_reader: Callable[[], FrameReader]) -> None:
        self._open_reader = open_reader
        self._reader: FrameReader | None = None
        self._index = -1
        self._frame: QImage | None = None
        self.frame_count: int | None = None

    def _rewind(self) -> None:
        self._reader = self._open_reader()
        self._index = -1
        self._frame = None

    def frame(self, index: int) -> QImage | None:
        """Image d'indice `index` (modulo la longueur du GIF), None si le GIF est illisible."""
        if self.frame_count == 0:
            return None
        if self.frame_count is not None:
            index %= self.frame_count
        if self._reader is None or index < self._index:
            self._rewind()
        while self._index < index:
            assert self._reader is not None
            image = self._reader.read()
            if image.isNull():
                # Fin du fichier : on connaît maintenant sa longueur, on reprend au début.
                self.frame_count = self._index + 1
                if self.frame_count == 0:
                    logger.warning("%s illisible : le malus MLG ne fait rien.", GIF_FILENAME)
                    return None
                return self.frame(index)
            self._frame = image
            self._index += 1
        return self._frame


@register
class MlgGif(Malus):
    key = "mlg_fullscreen"
    label = "MLG"
    description = "Un GIF « MLG » plein de couleurs au milieu de l'écran."
    default_duration_ms = 6000
    fade_in_ms = 0
    fade_out_ms = 0

    def setup(self) -> None:
        gif_path = resource_path(GIF_FILENAME)
        self.stream: GifStream | None = None
        if not gif_path.exists():
            logger.warning("%s introuvable (%s) : le malus MLG ne fait rien.", GIF_FILENAME, gif_path)
            return
        self.stream = GifStream(lambda: _open_qt_reader(gif_path))

    def paint(self, painter: QPainter, elapsed_ms: int) -> None:
        if self.stream is None:
            return
        image = self.stream.frame(elapsed_ms // FRAME_DELAY_MS)
        if image is None:
            return
        scale = self.ctx.scale
        width, height = image.width() * scale, image.height() * scale
        center = QPointF(self.ctx.width / 2, self.ctx.height / 2)
        painter.drawImage(QRectF(center.x() - width / 2, center.y() - height / 2, width, height), image)
