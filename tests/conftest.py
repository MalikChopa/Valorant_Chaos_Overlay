"""Configuration commune des tests : Qt sans écran (plateforme « offscreen »).

Doit tourner avant toute création de QApplication : pytest charge conftest.py en premier.
"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
