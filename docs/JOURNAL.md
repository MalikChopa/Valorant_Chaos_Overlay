# Journal des jalons : Valorant Chaos Overlay
Dernière mise à jour : 2026-11-10.
## Lancer
Depuis `C:\Users\Abdel-Malik\Projects\Valorant_Chaos_Overlay` (Git Bash) :
```
.venv/Scripts/python -m pytest -q -p no:cacheprovider
.venv/Scripts/python -m mypy --strict --ignore-missing-imports chaos_overlay
.venv/Scripts/python -c "import chaos_overlay.malus, chaos_overlay.scheduler"
.venv/Scripts/python -c "import chaos_overlay.ui.dashboard, chaos_overlay.ui.overlay, chaos_overlay.app"
```
Lancement de l'application (ouvre l'overlay plein écran : seulement avec l'accord de Malik, jamais fait au J1) :
```
.venv/Scripts/python -m chaos_overlay
.venv/Scripts/python valorant_roulette.py
```
## État
| Jalon | État | Vérifié par Diapason |
|---|---|---|
| J1 Cœur (découpage, types, tests, bugs) | fait (non lancé sur le bureau) | oui (2026-11-10 : pytest 252 passed, mypy strict OK, imports sans fenêtre, grep API interdites vide) |
## J1 : Cœur
- Fait :
  - Lecture de CLAUDE.md, ARCHITECTURE.md, valorant_roulette.py (372 lignes, commit a74abcb).
  - API customtkinter 6.0.0 installée : les 8 classes et 2 fonctions utilisées existent, et chaque paramètre passé par l'ancien code figure dans la signature `__init__` (contrôle par `inspect.signature`). Aucune adaptation nécessaire.
  - Paquet `chaos_overlay/` selon §2 sans `config.py` ni `hotkey.py` : `__init__.py` (2.0.0), `__main__.py`, `app.py`, `paths.py`, `theme.py`, `scheduler.py`, `win32.py`, `malus/` (base + 11 modules + registre), `ui/` (`__init__.py`, `overlay.py`, `splash.py`, `dashboard.py`, `roulette.py`).
  - `valorant_roulette.py` : lanceur de 3 lignes qui appelle `chaos_overlay.app.main()`.
  - Bugs §4 : (1) état par instance de malus, `stop()` idempotent qui annule les `after` en attente et efface ses éléments ; (2) GIF chargé au premier déclenchement, 150 images au plus (`frames_needed(6000, 40)`), puis gardé en cache ; fichier absent : rien affiché + `logger.warning` ; (3) `win32.make_click_through(hwnd) -> bool` (relit le style pour vérifier), avertissement messagebox si False ; (4) plus de `os.chdir` ni de remplacement de stdout à l'import, tout est dans `main()` ; `crash_log.txt` écrit dans `app_dir()`.
  - HOME : lib `keyboard` gardée, fonction `register_home_hotkey()` dans `app.py`, même message d'avertissement mot pour mot.
  - Tests (`tests/`, sans fenêtre Tk) : `test_scheduler.py`, `test_registry.py`, `test_malus.py` (faux canvas + faux minuteur), `test_paths_win32.py` (faux user32), `test_parity.py` (ancien code contre nouveau). `tests/legacy_reference.py` = copie verbatim des lignes 236-251 et 262-361 de l'ancien fichier (extraite par `sed` avant remplacement, `git diff` vide vérifié avant).
- Critères mesurés :
  - `.venv/Scripts/python -m pytest -q -p no:cacheprovider` → `252 passed in 2.39s`.
  - `.venv/Scripts/python -m mypy --strict --ignore-missing-imports chaos_overlay` → `Success: no issues found in 25 source files`. Même résultat avec `--warn-unreachable` en plus. Sans `--ignore-missing-imports` : 4 erreurs, toutes `import-untyped` sur `customtkinter` (3) et `keyboard` (1), rien d'autre.
  - `.venv/Scripts/python -c "import chaos_overlay.malus, chaos_overlay.scheduler"` → code de sortie 0, aucune sortie, aucune fenêtre.
  - `.venv/Scripts/python -c "import chaos_overlay.ui.dashboard, chaos_overlay.ui.overlay, chaos_overlay.app"` → code de sortie 0 ; `tkinter._default_root` vaut `None` après l'import (aucune racine Tk créée).
  - Tests d'import en sous-processus : pas de Tk, pas de chdir, stdout/stderr inchangés, `scheduler` n'importe pas tkinter.
  - Parité : 11 malus × 5 graines × 3 tailles d'écran (1920×1080, 2560×1440, 1280×720) + roulette (4 listes × 5 graines) : la liste complète des appels canvas (type, coordonnées, couleurs, polices, textes, effacements, instant en ms) est identique entre l'ancien et le nouveau code. Contrôle par mutation (script hors projet) : changer `HALF_SIZE`, la probabilité du moustique ou le nombre de pings fait bien échouer la comparaison.
  - Grep : `windll` n'apparaît que dans `win32.py` ; aucun SendInput, keybd_event, mouse_event, ReadProcessMemory, capture d'écran ni chdir dans le paquet.
- Non mesuré :
  - Rendu visuel réel, ouverture du Dashboard, splash, HOME, click-through sur une vraie fenêtre : application non lancée (pas d'accord pour un lancement bureau).
  - Mémoire réelle du GIF (150 images au lieu d'environ 608) : non mesurée.
  - Durée du chargement des 150 images au premier déclenchement du malus MLG (petit gel possible à ce moment-là, plus au démarrage) : non mesurée.
  - Comportement de `register_home_hotkey` et des messagebox : non exécutés.
- Tableau de parité (lignes de l'ancien `valorant_roulette.py`) :

| Malus | Ancien code (lignes) | Nouveau fichier | Résultat |
|---|---|---|---|
| flashbang | 262-264 | `chaos_overlay/malus/flashbang.py` | identique (test de parité) |
| tunnel_vision | 266-274 | `chaos_overlay/malus/tunnel_vision.py` | identique (test de parité) |
| hud_blocker | 276-282 | `chaos_overlay/malus/hud_blocker.py` | identique (test de parité) |
| fake_crosshair | 284-290 | `chaos_overlay/malus/fake_crosshair.py` | identique (test de parité) |
| scanlines | 292-294 | `chaos_overlay/malus/scanlines.py` | identique (test de parité) |
| mlg_fullscreen | 347-361 (+ chargement 216-225, appel 86) | `chaos_overlay/malus/mlg_gif.py` | rendu identique (test de parité, GIF long et court) ; écart voulu §4.2 : chargement au 1er déclenchement, 150 images max (l'ancien code n'affichait jamais l'image d'indice ≥ 150 : vérifié par test) |
| fake_crash | 296-301 | `chaos_overlay/malus/fake_crash.py` | identique (test de parité) |
| blind_spot | 303-305 | `chaos_overlay/malus/blind_spot.py` | identique (test de parité) |
| paranoia | 307-316 | `chaos_overlay/malus/paranoia.py` | identique (test de parité, même ordre des tirages) |
| screen_crack | 318-326 | `chaos_overlay/malus/screen_crack.py` | identique (test de parité) ; `create_line(coords)` au lieu de `create_line(*coords)`, équivalent car tkinter aplatit les arguments (`Canvas._create` appelle `_flatten`, lu dans la source tkinter du venv) |
| mosquito | 328-345 | `chaos_overlay/malus/mosquito.py` | identique (test de parité sur 15 s) ; écart voulu §4.1 : état par instance |
| roulette (pas un malus) | 231-251 | `chaos_overlay/ui/roulette.py` + `scheduler.py` | identique (test de parité, instant du malus = somme des 30 délais + 1500 ms) |

- Écarts à l'architecture et décisions :
  - `REGISTRY` et `@register` sont définis dans `malus/base.py` et réexportés par `malus/__init__.py` (évite l'import circulaire entre `__init__` et les modules de malus). `chaos_overlay.malus.REGISTRY` reste le point d'accès.
  - `Malus.__init__(duration_ms=None)` : durée par défaut = `default_duration_ms`, réglable (prépare J2 `durations_ms`). `start()` deux fois sur la même instance lève `RuntimeError`. Méthodes internes `_draw`, `_track`, `_schedule` ; propriété `is_running`.
  - `scheduler` contient aussi `roulette_pool()` (liste ou `["rien"]`) et `display_name()` (`"tunnel_vision"` → `"TUNNEL VISION"`). `pick()` consomme le hasard exactement comme l'ancien `random.choice(["rien"])`.
  - `parse_frequency` refuse les chiffres non ASCII (`"²"`) : l'ancien `isdigit()` les acceptait puis `int()` levait une erreur dans le callback.
  - `win32.py` contient aussi `toplevel_hwnd()` (le `GetParent` de l'ancien code), pour que `ctypes.windll` reste dans ce seul fichier.
  - `NullWriter` remplacé par `open(os.devnull, ...)` dans `main()` quand stdout/stderr valent `None` (même effet, objet fichier complet).
  - `logging.basicConfig` (niveau INFO, vers stderr) dans `main()`. En exe sans console, stderr va vers devnull : l'avertissement « mlg.gif introuvable » n'est donc pas visible pour l'utilisateur. Un fichier journal pourrait venir au J2 (avertissements de config) : décision à prendre par Diapason.
  - `execute_malus` relance le minuteur dans un `finally` : si un malus plante, le chaos continue (l'ancien code s'arrêtait). L'erreur reste signalée par Tk.
  - Message du nouvel avertissement click-through (texte nouveau, aucun texte d'origine) : « Impossible de rendre l'overlay transparent aux clics. Les malus affichés risquent de bloquer la souris : ferme l'application si c'est le cas. »
  - Ordre de démarrage conservé : HOME (et son avertissement) avant la mise en place de l'overlay, puis splash puis Dashboard.
  - mypy : pas de fichier de config (pas le mien) ; options sur la ligne de commande ci-dessus, à reporter dans `pyproject.toml` au J3 (idéalement `ignore_missing_imports` limité à `customtkinter` et `keyboard`).
  - `tests/legacy_reference.py` porte `# mypy: ignore-errors` (code d'origine recopié tel quel, hors périmètre mypy).
- Bugs connus :
  - Hérités, non corrigés (hors §4) : le rappel HOME de `keyboard` appelle `root.after` depuis un autre thread (corrigé par la file d'attente du J2) ; `screen_crack` lève `ValueError` si l'écran fait moins de 600×400 px (comme avant ; le minuteur repart grâce au `finally`).
  - Artefact : `.mypy_cache/` créé à la racine par mypy (il contient son propre `.gitignore`) ; `.gitignore` du projet prévu au J3.
  - `docs/FICHE.md` apparaît modifié dans `git status` : pas par moi (je n'y ai pas écrit).
