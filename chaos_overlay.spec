# -*- mode: python ; coding: utf-8 -*-
# Build : .venv\Scripts\python -m PyInstaller --noconfirm chaos_overlay.spec
# Un seul exe, sans console ; mlg.gif est embarqué à la racine du bundle (lu via sys._MEIPASS).
import sys

# Seuls QtCore, QtGui et QtWidgets sont utilisés : on exclut le reste de Qt et tkinter pour alléger l'exe.
a = Analysis(
    ["chaos_overlay/__main__.py"],
    pathex=["."],
    binaries=[],
    datas=[("mlg.gif", ".")],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "PySide6.QtNetwork",
        "PySide6.QtQml",
        "PySide6.QtQuick",
        "PySide6.QtSql",
        "PySide6.QtTest",
        "PySide6.QtOpenGL",
        "PySide6.QtPdf",
        "PySide6.QtSvg",
        "PySide6.QtDBus",
    ],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="chaos_overlay",
    debug=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    # Icône de l'exe (régénérable avec scripts/make_icon.py) ; format .ico propre à Windows.
    icon="assets/chaos_overlay.ico" if sys.platform == "win32" else None,
)
