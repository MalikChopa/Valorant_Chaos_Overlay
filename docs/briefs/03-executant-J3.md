Project: Valorant Chaos Overlay — passive desktop overlay for streamers (random visual handicaps over the screen). Folder: C:\Users\Abdel-Malik\Projects\Valorant_Chaos_Overlay (run all commands from this folder). Today's date: 2026-11-10. Language: French (README, JOURNAL, report).
Read first: CLAUDE.md, docs/ARCHITECTURE.md §1, §2, §5 "J3", docs/JOURNAL.md ("Lancer" section and J1/J2 summaries), the current README.md (whole, 50 lines), docs/FICHE.md §2 and §4 (decisions, including the mlg.gif row). Look at the code only by grep (module names, malus keys, durations in chaos_overlay/malus/*.py, config fields in chaos_overlay/config.py).
Useful user context: Windows 11, Python 3.10.11; GitHub repo MalikChopa/Valorant_Chaos_Overlay (public); existing GitHub releases v1.0.0 and v1.1.0 (2026-04-07) were built from the OLD single-file code.
You write ONLY: pyproject.toml, .gitignore, chaos_overlay.spec, LICENSE, README.md, docs/JOURNAL.md (section J3 + state table). Build outputs build/ and dist/ may be created by your build run (they must be git-ignored). Do not touch: chaos_overlay/, tests/, valorant_roulette.py, docs/FICHE.md, docs/ARCHITECTURE.md, docs/HANDOFF.md, CLAUDE.md, mlg.gif, .venv/ (install or uninstall nothing). In parallel: nobody.
Progress: section J3 of docs/JOURNAL.md, created early, updated at each sub-step.
Budget: about 200 k tokens. Reached: write your file and report TERMINÉ AVEC RÉSERVES.
Project dependencies allowed: those in .venv only (`.venv/Scripts/python -m pip freeze` gives exact versions). Use `.venv/Scripts/python`.
Filter your commands' output (grep, tail, head).

Role: writer and build engineer. SOLE writer of the files above.

HARD LIMITS: never launch the built .exe or the app window. Never launch Valorant. No git push, no release, no commit (Diapason commits). No game screenshots or images. Do not invent facts: every claim in the README must be true of the current code; what is not verified is said so.

To deliver (J3):
1. pyproject.toml: `[project]` name `valorant-chaos-overlay`, version from chaos_overlay/__init__.py (`2.0.0`, static is fine), `requires-python = ">=3.10"`, dependencies `customtkinter==6.0.0` (and its runtime deps only if needed — check `pip show customtkinter`), optional dev group `pytest`, `mypy`, `pyinstaller` with the exact versions installed; `[project.scripts]` or `gui-scripts` entry `chaos-overlay = "chaos_overlay.app:main"`; `[tool.pytest.ini_options]` (testpaths = ["tests"]); `[tool.mypy]` reproducing the J1/J2 command (strict, customtkinter ignore_missing_imports via an override, not global if possible). Build backend: setuptools, package discovery limited to chaos_overlay. Do not run `pip install -e .` (that would modify .venv).
2. .gitignore: .venv/, __pycache__/, .mypy_cache/, .pytest_cache/, build/, dist/, *.log, chaos_config.json, crash_log.txt.
3. chaos_overlay.spec: one-file, windowed (no console), entry valorant_roulette.py, exe name `valorant_roulette` (keeps the release name), datas embeds mlg.gif at the bundle root (resource_path reads it from sys._MEIPASS). Build it: `.venv/Scripts/python -m PyInstaller --noconfirm chaos_overlay.spec`. Verify mlg.gif is inside the exe with the archive viewer (`.venv/Scripts/pyi-archive_viewer --list dist/valorant_roulette.exe` or the equivalent for PyInstaller 6.22, filtered with grep) and record the exe size. Do NOT run the exe.
4. LICENSE: MIT, `Copyright (c) 2026 MalikChopa`. Add a short note in the README that mlg.gif is NOT covered by this licence (third-party, source unknown).
5. README.md (French, réponses claires, niveau intermédiaire), replacing the old one:
   - title + 1-line pitch; badges: Python 3.10+, Windows, licence MIT, and a "passif" badge instead of "Vanguard Safe";
   - section « Ce que fait l'overlay / ce qu'il ne fait pas » : passif ; transparent aux clics (styles de fenêtre Win32) ; touche HOME via RegisterHotKey (raccourci Windows standard, plus besoin du mode administrateur) ; aucune lecture mémoire, injection, macro, capture, ni interaction avec le jeu ou Vanguard. Honest sentence: no guarantee from Riot; the tool only draws over the screen; use at your own risk (wording yours, short, no fear-mongering);
   - table of the 11 malus with key, effect and duration taken from the code (grep), in registry order;
   - configuration: chaos_config.json next to the exe/project, fields, bounds (frequency 1–3600 s, durations 500–60000 ms), fallback on defaults; log file chaos_overlay.log;
   - installation from source with venv (Windows commands: `py -3.10 -m venv .venv`, `.venv\Scripts\activate`, `pip install -e .[dev]` or the pyproject equivalent), run (`python -m chaos_overlay`), tests (`pytest`), types (`mypy`), build (`pyinstaller chaos_overlay.spec`);
   - releases: say that v1.0.0/v1.1.0 were built from the previous version and a new release is not published yet;
   - an architecture diagram in a ```mermaid block (GitHub renders it): app → dashboard/overlay/roulette/splash, scheduler, config, hotkey, malus registry → 11 malus modules, win32; plus a short « Ajouter un malus » how-to (new file in chaos_overlay/malus/, @register, key, default_duration_ms, _draw; add the import in malus/__init__.py if needed — check how J1 registers them);
   - credits: « Made by Chupa » (kept from the app); mlg.gif: « trouvé sur un site de GIF, source inconnue, droits non vérifiés ; non couvert par la licence MIT » (decision of the user, 2026-11-10);
   - no screenshots, no game images, no Riot logos.
   The clone URL is https://github.com/MalikChopa/Valorant_Chaos_Overlay.git.

Criteria (to measure):
- `.venv/Scripts/python -m pytest -q` (now configured by pyproject) → still all green (310); summary line in JOURNAL.
- `.venv/Scripts/python -m mypy` with no arguments, reading pyproject → Success on chaos_overlay.
- pyproject is valid TOML: `.venv/Scripts/python -c "import tomli; tomli.load(open('pyproject.toml','rb'))"`.
- Build OK, mlg.gif present in the archive listing, exe size recorded; build/ and dist/ ignored (`git status --short` shows neither).
- README: every malus key in the table exists in REGISTRY (check by a small python command that compares), no "dance.gif", no "VOTRE_NOM", no "3.13".
- Not measurable here: the exe actually running. Write "non mesuré".

Final report: 10 lines at most; first line a status: TERMINÉ / TERMINÉ AVEC RÉSERVES / BESOIN DE CONTEXTE / BLOQUÉ. Then result, confidence, what is not verified. Three failures on the same error: stop and report.
