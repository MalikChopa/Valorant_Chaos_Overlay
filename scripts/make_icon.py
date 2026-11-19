"""Régénère assets/chaos_overlay.ico (icône de l'exe) à partir de chaos_overlay/ui/icon.py.

Usage : python scripts/make_icon.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QGuiApplication  # noqa: E402

from chaos_overlay.ui.icon import render_icon  # noqa: E402

OUTPUT = Path(__file__).resolve().parent.parent / "assets" / "chaos_overlay.ico"


def main() -> int:
    app = QGuiApplication(sys.argv)  # nécessaire pour dessiner
    OUTPUT.parent.mkdir(exist_ok=True)
    if not render_icon(256).save(str(OUTPUT)):  # format déduit de l'extension .ico
        print(f"Échec de l'écriture de {OUTPUT}", file=sys.stderr)
        return 1
    print(f"Écrit : {OUTPUT}")
    del app
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
