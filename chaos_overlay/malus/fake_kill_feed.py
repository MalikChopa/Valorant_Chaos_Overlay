"""Fake kill feed : de faux éliminations défilent en haut à droite, souvent contre « TOI »."""

from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen

from chaos_overlay import theme
from chaos_overlay.malus.base import Malus, register

PLAYERS = ["xX_Sn1per_Xx", "Baguette", "NoScopeNinja", "Croissant", "TryHard42", "Tartiflette", "ClutchKing", "Raclette"]
WEAPONS = ["AWP", "AK", "SNIPER", "PISTOL", "KNIFE", "SHOTGUN"]
YOU = "TOI"
ENTRY_COUNT = 6
ENTRY_INTERVAL_MS = 700
MAX_VISIBLE = 5
YOU_CHANCE = 0.6


@register
class FakeKillFeed(Malus):
    key = "fake_kill_feed"
    label = "Faux kill feed"
    description = "De fausses éliminations défilent en haut à droite… et tu meurs souvent."
    default_duration_ms = 6000

    def setup(self) -> None:
        rng = self.ctx.rng
        self.entries: list[tuple[str, str, str]] = []
        for _ in range(ENTRY_COUNT):
            killer, victim = rng.sample(PLAYERS, 2)
            if rng.random() < YOU_CHANCE:
                victim = YOU
            self.entries.append((killer, rng.choice(WEAPONS), victim))

    def visible_entries(self, elapsed_ms: int) -> list[tuple[str, str, str]]:
        """Les lignes affichées à cet instant : une de plus toutes les 700 ms, 5 au plus."""
        shown = min(len(self.entries), elapsed_ms // ENTRY_INTERVAL_MS + 1)
        return self.entries[max(0, shown - MAX_VISIBLE) : shown]

    def paint(self, painter: QPainter, elapsed_ms: int) -> None:
        ctx = self.ctx
        font = QFont(theme.FONT_FAMILY)
        font.setPixelSize(ctx.px(18))
        font.setBold(True)
        painter.setFont(font)
        metrics = QFontMetrics(font)
        row_height = ctx.px(34)
        margin = ctx.px(20)
        top = ctx.px(90)
        for row, (killer, weapon, victim) in enumerate(self.visible_entries(elapsed_ms)):
            text = f"{killer}   [{weapon}]   {victim}"
            width = metrics.horizontalAdvance(text) + 2 * margin
            box = QRectF(ctx.width - margin - width, top + row * (row_height + ctx.px(4)), width, row_height)
            painter.setPen(QPen(QColor(theme.ACCENT), ctx.px(2)) if victim == YOU else Qt.PenStyle.NoPen)
            painter.setBrush(QColor(15, 25, 35, 200))
            painter.drawRect(box)
            painter.setPen(QColor(theme.ACCENT) if victim == YOU else QColor(theme.TEXT))
            painter.drawText(box, Qt.AlignmentFlag.AlignCenter, text)
