# -*- mode: python ; coding: utf-8 -*-
# Build : .venv/Scripts/python -m PyInstaller --noconfirm chaos_overlay.spec
# Un seul exe, sans console ; mlg.gif est embarqué à la racine du bundle (lu via sys._MEIPASS).
a = Analysis(
    ["valorant_roulette.py"],
    pathex=["."],
    binaries=[],
    datas=[("mlg.gif", ".")],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="valorant_roulette",
    debug=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
)
