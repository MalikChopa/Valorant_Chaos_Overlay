Project: Valorant Chaos Overlay — passive desktop overlay for streamers (random visual handicaps over the screen). Folder: C:\Users\Abdel-Malik\Projects\Valorant_Chaos_Overlay (run all commands from this folder). Today's date: 2026-11-10. Language: French (for docs/JOURNAL.md and your report; code identifiers and comments may stay English or French, keep the existing French UI strings exactly).
Read first: CLAUDE.md, then docs/ARCHITECTURE.md (whole, ~90 lines), then valorant_roulette.py (whole, 372 lines: it is the behaviour reference). docs/FICHE.md only if a scope doubt arises.
Useful user context: Windows 11, Python 3.10.11, Git Bash. Junior developer: the code must stay readable for him (clear names, short docstrings, no clever metaprogramming).
You write ONLY: chaos_overlay/ (new package), tests/ (new), valorant_roulette.py (replaced by a 3-line launcher), docs/JOURNAL.md. Do not touch: docs/FICHE.md, docs/ARCHITECTURE.md, docs/HANDOFF.md, CLAUDE.md, README.md, mlg.gif (user's original, read only), .venv/ (do not install anything). In parallel: nobody.
Progress: create docs/JOURNAL.md early (template below) and complete section J1 as you go; a cut must lose nothing.
Budget: about 400 k tokens. Reached: write your file and report TERMINÉ AVEC RÉSERVES.
Project dependencies allowed: those already in .venv (customtkinter 6.0.0, keyboard 0.13.5, pytest 9.2.0, mypy 2.4.1, pyinstaller 6.22.3). Nothing else. Use `.venv/Scripts/python`.
Filter your commands' output (grep, tail, head): no full output in your context.

Role: developer of the project; Python 3.10 (no 3.11+ syntax: no `Self`, no `except*`, no `tomllib`), tkinter + customtkinter 6.0.0, ctypes. You are the SOLE writer of the files listed above.

HARD LIMITS (project rule, non-negotiable): the overlay stays strictly passive. Do not add any memory reading, process inspection, input injection (SendInput, keybd_event, mouse events), screen capture, game/window detection, or anything touching Vanguard/anti-cheat. Do NOT launch the application window (no `python -m chaos_overlay`, no running valorant_roulette.py): there is no approved desktop run yet. Never launch Valorant. Do not commit, Diapason commits.

To deliver (J1, see ARCHITECTURE §2, §3, §4, §5 "J1"):
- Package chaos_overlay/ per §2 WITHOUT config.py and hotkey.py (J2). HOME hotkey keeps using the `keyboard` lib, moved into app.py (or a small function there), same warning message if it fails.
- One module per malus in chaos_overlay/malus/, registered in REGISTRY in the current display order; each reproduces the current visuals exactly (coordinates, colours, fonts, texts, durations, random ranges).
- Bug fixes of §4: per-instance state (overlap), lazy + limited GIF loading (150 frames, 40 ms), click-through returning bool + warning, no import side effects, crash_log.txt in app_dir().
- valorant_roulette.py becomes a launcher calling chaos_overlay.app.main().
- tests/ with the J1 tests listed in ARCHITECTURE §5 (fake canvas object for stop() tests; no Tk root created in tests).
- Typing: annotations everywhere; add a minimal mypy config (a `mypy.ini` or `setup.cfg` is NOT yours to create: put the settings on the command line and record the exact command in JOURNAL; J3 will move them into pyproject.toml).

Criteria (to measure; never announce an unmeasured figure):
- `.venv/Scripts/python -m pytest -q` → all green; paste the summary line in JOURNAL.
- `.venv/Scripts/python -m mypy --strict --ignore-missing-imports chaos_overlay` (or a stricter per-module variant) → "Success"; paste the line.
- `.venv/Scripts/python -c "import chaos_overlay.malus, chaos_overlay.scheduler"` → no error and no window.
- `.venv/Scripts/python -c "import chaos_overlay.ui.dashboard, chaos_overlay.ui.overlay, chaos_overlay.app"` → imports without opening a window (verifies customtkinter 6 API names exist; if an API used by the old code no longer exists in 6.0.0, adapt and note it).
- Behaviour parity: in JOURNAL, a table of the 11 malus with old line numbers → new file, and "identique" or the deviation.
- Not measurable here (no window run): visual rendering, real memory use. Write "non mesuré".

JOURNAL template (create docs/JOURNAL.md, in French):
```
# Journal des jalons : Valorant Chaos Overlay
Dernière mise à jour : <date>.
## Lancer
<commandes exactes : tests, mypy, lancement>
## État
| Jalon | État | Vérifié par Diapason |
|---|---|---|
| J1 Cœur (découpage, types, tests, bugs) | en cours | non |
## J1 : Cœur
- Fait : …
- Critères mesurés : …
- Non mesuré : …
- Écarts à l'architecture et décisions : …
- Bugs connus : …
```
Diapason may send you bugs afterwards: fix them first.

Final report: 10 lines at most (the file is the truth). The first line is a status: TERMINÉ / TERMINÉ AVEC RÉSERVES / BESOIN DE CONTEXTE / BLOQUÉ. Then: the result, the confidence, what is not verified or not measured. Three failures on the same error: stop and report.
