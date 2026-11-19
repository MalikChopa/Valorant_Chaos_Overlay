"""Roulette affichée sur l'overlay avant chaque malus (rythme donné par scheduler.roulette_delays).

`Roulette` est l'état (texte courant, résultat ou non) et sa progression dans le temps ;
`paint_roulette` le dessine. L'overlay appelle le second à chaque image.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen

from chaos_overlay import scheduler, theme

# Planifie un appel : la signature de QTimer.singleShot(ms, fonction).
Scheduler = Callable[[int, Callable[[], None]], object]

BOX_X = 20
BOX_WIDTH = 350
BOX_HEIGHT = 80
FONT_SIZE = 28


class Roulette:
    """Fait défiler des noms de malus de plus en plus lentement, puis affiche le résultat."""

    def __init__(
        self,
        after: Scheduler,
        rng: random.Random,
        label_of: Callable[[str], str],
        on_change: Callable[[], None] = lambda: None,
    ) -> None:
        self.after = after
        self.rng = rng
        self.label_of = label_of
        self.on_change = on_change
        self.visible = False
        self.text = ""
        self.is_result = False

    def spin(self, final_key: str, pool: Sequence[str], on_done: Callable[[str], None]) -> None:
        """Lance la roulette ; à la fin, la cache et appelle on_done(final_key)."""
        delays = scheduler.roulette_delays()
        names = list(pool)

        def show(text: str, is_result: bool) -> None:
            self.visible, self.text, self.is_result = True, text, is_result
            self.on_change()

        def finish() -> None:
            self.visible, self.text, self.is_result = False, "", False
            self.on_change()
            on_done(final_key)

        def step(index: int) -> None:
            if index < len(delays):
                show(self.label_of(self.rng.choice(names)).upper(), is_result=False)
                self.after(delays[index], lambda: step(index + 1))
            else:
                show(f">> {self.label_of(final_key).upper()} <<", is_result=True)
                self.after(scheduler.ROULETTE_RESULT_PAUSE_MS, finish)

        step(0)


def paint_roulette(painter: QPainter, roulette: Roulette, scale: float, screen_height: int) -> None:
    """Dessine la boîte de la roulette sur le bord gauche, au tiers de la hauteur."""
    if not roulette.visible:
        return
    box = QRectF(BOX_X * scale, screen_height / 3, BOX_WIDTH * scale, BOX_HEIGHT * scale)
    painter.save()
    painter.setPen(QPen(QColor(theme.ACCENT), max(1.0, 3 * scale)))
    painter.setBrush(QColor(theme.BACKGROUND))
    painter.drawRoundedRect(box, 6 * scale, 6 * scale)
    font = QFont(theme.FONT_FAMILY)
    font.setPixelSize(max(1, round(FONT_SIZE * scale)))
    font.setBold(True)
    painter.setFont(font)
    painter.setPen(QColor(theme.ACCENT if roulette.is_result else theme.TEXT))
    painter.drawText(box, Qt.AlignmentFlag.AlignCenter, roulette.text)
    painter.restore()
