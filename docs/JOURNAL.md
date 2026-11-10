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
| J1 Cœur (découpage, types, tests, bugs) | fait (lancé sur le bureau le 2026-11-10, validé par Malik) | oui (2026-11-10 : pytest 252 passed, mypy strict OK, imports sans fenêtre, grep API interdites vide) |
| J2 Config JSON, HOME sans admin, journal | fait (lancé sur le bureau le 2026-11-10 ; HOME avec fenêtre admin non mesurée) | oui (2026-11-10 : pytest 310 passed, mypy strict OK 28 fichiers, plus de lib keyboard, grep API interdites vide) |
| J3 Packaging, .spec, README, licence | fait (exe construit, non lancé) | oui (2026-11-10 : pytest 310, mypy OK, mlg.gif présent dans l exe, README relu : 2 corrections faites) |
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
## J2 : Config + HOME sans admin
- Fait :
  - Lecture : CLAUDE.md, ARCHITECTURE.md §3 et §5, JOURNAL §J1, `app.py`, `ui/dashboard.py`, `paths.py`, `malus/base.py`, `win32.py`, tests existants.
  - `chaos_overlay/config.py` (pur : n'importe pas tkinter au chargement ; le registre des malus est importé seulement à l'appel) : dataclass `Config` (`frequency_s` 60, `enabled` tout à True, `durations_ms` = `default_duration_ms` de chaque malus, `hotkey` "home"), `config_path()` = `app_dir() / "chaos_config.json"`, `load(path)`, `save(config, path) -> bool`, `clamp_frequency()`. Lecture champ par champ : un champ invalide reprend sa valeur par défaut avec un avertissement ; fichier absent : valeurs par défaut sans avertissement ; JSON invalide, UTF-8 invalide ou racine qui n'est pas un objet : tout par défaut + avertissement ; clés inconnues ignorées ; clés de malus manquantes complétées. `true`/`false` ne comptent pas comme des entiers. Écriture : fichier temporaire dans le même dossier, `fsync`, puis `os.replace` ; en cas d'`OSError` : avertissement, temporaire supprimé, `False`.
  - `chaos_overlay/hotkey.py` : `HomeHotkey(callback, after, user32=None)`, `start() -> bool`, `stop()`, `poll()`. Thread démon : `RegisterHotKey(None, 1, MOD_NOREPEAT, VK_HOME)` puis boucle `GetMessageW` ; WM_HOTKEY (id 1) → jeton dans une `queue.Queue` ; `GetMessageW` = 0 (WM_QUIT) ou -1 (erreur) → sortie de boucle puis `UnregisterHotKey` dans le même thread. Côté Tk : `root.after(100, ...)` vide la file et appelle le callback dans le thread Tk. `stop()` : arrêt de la scrutation, `PostThreadMessageW(WM_QUIT)`, `join(1 s)`.
  - `chaos_overlay/logs.py` : `setup_logging()` = console si `sys.stderr` existe + `RotatingFileHandler(app_dir() / "chaos_overlay.log", 256 Ko, 2 sauvegardes, UTF-8)` ; échec d'ouverture du fichier : avertissement sur la console, pas de plantage ; rappel sans doublon de handlers.
  - `chaos_overlay/app.py` : config chargée au démarrage (fréquence et cases du Dashboard), bouton « ▶ DÉMARRER LE CHAOS » → `start_clicked()` = `save_config()` puis `start_timer()` ; chaque malus reçoit `durations_ms[key]` ; `HomeHotkey` remplace `register_home_hotkey` et la lib `keyboard` ; nouvel avertissement « La touche HOME est déjà utilisée par un autre programme : le Dashboard ne pourra pas être rouvert en jeu. » ; `setup_logging()` remplace `basicConfig` ; `app.close()` (arrêt de HOME) dans un `finally` après `mainloop()` ; l'erreur fatale est aussi journalisée avant `crash_log.txt`.
  - `ui/dashboard.py` : non modifié (il lit déjà `timer_interval` et `malus_states`, que l'app remplit depuis la config ; aucun widget ajouté).
  - `win32.py` : docstring seule (mention de hotkey.py).
  - Tests ajoutés : `tests/test_config.py` (37 cas : aller-retour, fichier absent, JSON corrompu, UTF-8 invalide, racine non-objet, mauvais types, bornes, clé inconnue, clé de malus manquante, hotkey, sauvegarde atomique sans temporaire, échec d'écriture, échec de `os.replace`, import sans tkinter), `tests/test_hotkey.py` (10 : faux user32, aucun vrai raccourci système ; `poll()` = un appel par jeton, `start()` False si RegisterHotKey renvoie 0, cycle complet start/WM_HOTKEY/stop, erreur GetMessageW, imports sans fenêtre ni lib `keyboard`), `tests/test_logs.py` (7 : fichier dans tmp_path, chemin inaccessible, sans stderr, sans doublon), `tests/test_app_config.py` (4 : sauvegarde des valeurs du Dashboard, bornage de la fréquence, ordre sauvegarde puis minuteur, durée configurée transmise au malus). Tests J1 inchangés.
- Critères mesurés :
  - `.venv/Scripts/python -m pytest -q -p no:cacheprovider` → `310 passed in 2.99s` (252 du J1 + 58). `tests/test_hotkey.py` lancé 5 fois de suite : 5 × `10 passed`.
  - `.venv/Scripts/python -m mypy --strict --ignore-missing-imports chaos_overlay` → `Success: no issues found in 28 source files`. Sans `--ignore-missing-imports` : 3 erreurs, toutes `import-untyped` sur `customtkinter` (celle de `keyboard` a disparu).
  - `grep -rn "keyboard" chaos_overlay` → une seule ligne : la docstring de `hotkey.py` (« remplace la lib `keyboard` »), aucun import.
  - `grep -rnE "SetWindowsHookEx|SendInput|keybd_event|mouse_event|ReadProcessMemory|OpenProcess" chaos_overlay` → vide.
  - `.venv/Scripts/python -c "import sys, tkinter, chaos_overlay.app, chaos_overlay.hotkey, chaos_overlay.config; ..."` → code 0, `tkinter._default_root` = None, `keyboard` absent de `sys.modules`.
  - Aucun `chaos_config.json` ni `chaos_overlay.log` créé à la racine par les tests (vérifié par `ls`).
- Non mesuré :
  - HOME qui se déclenche pour de vrai (aucun raccourci système enregistré, application non lancée).
  - Comportement quand une fenêtre lancée en administrateur a le focus (UIPI) : non mesuré.
  - Affichage réel des messagebox, du Dashboard rempli par la config, écriture réelle de `chaos_config.json` et `chaos_overlay.log` à côté de l'exe.
- Écarts au brief et décisions :
  - Signature `HomeHotkey(callback, after, user32=None)` au lieu de `HomeHotkey(callback)` : `after` (= `root.after`) sert à la scrutation de 100 ms ; `user32` permet le faux objet des tests.
  - `GetCurrentThreadId` non appelé : `threading.get_native_id()` donne le même identifiant Windows sans charger kernel32.
  - user32 chargé par `ctypes.WinDLL("user32", use_last_error=True)` dans `hotkey.py` (instance à part, signatures `argtypes`/`restype` posées) : `ctypes.windll` reste dans `win32.py` seul, mais `hotkey.py` est un second fichier qui appelle user32 (écart à ARCHITECTURE §2 « seul fichier qui appelle ctypes.windll » : à trancher par Diapason).
  - `MOD_NOREPEAT` (comme demandé par le brief ; ARCHITECTURE §5 disait 0) : un appui maintenu ne répète pas l'ouverture.
  - Fréquence saisie au-dessus de 3600 s : bornée à 3600 au clic « Démarrer » (minuteur et fichier cohérents), info journalisée. Avant, la valeur était prise telle quelle.
  - `hotkey` accepte « HOME » (majuscules, espaces) comme « home ».
  - Constantes hotkey gardées dans `hotkey.py` (pas dans `win32.py`).
  - `app.DEFAULT_FREQUENCY_S` gardé (alias de `config.DEFAULT_FREQUENCY_S`).
- Bugs connus :
  - Le bug hérité « callback HOME appelé depuis un autre thread » est corrigé (file + `root.after`).
  - Si le thread HOME ne répond pas en 2 s au démarrage, `start()` renvoie False et l'avertissement s'affiche alors que la touche pourrait finir par marcher : cas non observé.

## J3 : Packaging, README, licence
- Fait :
  - `pyproject.toml` (setuptools, paquet `chaos_overlay*` seul ; `customtkinter==6.0.0` ; dev : pytest 9.2.0, mypy 2.4.1, pyinstaller 6.22.3 ; gui-script `chaos-overlay` ; pytest `testpaths=["tests"]` + `-p no:cacheprovider` ; mypy `strict`, `files=["chaos_overlay"]`, `ignore_missing_imports` seulement via override sur `customtkinter`). `.gitignore`, `LICENSE` (MIT, MalikChopa), `chaos_overlay.spec` (one-file, sans console, nom `valorant_roulette`, `datas=[("mlg.gif", ".")]`), `README.md` réécrit.
- Critères mesurés :
  - `.venv/Scripts/python -m pytest -q` → `310 passed in 3.23s`.
  - `.venv/Scripts/python -m mypy` (sans argument) → `Success: no issues found in 28 source files`.
  - `tomli.load(pyproject.toml)` → OK.
  - `.venv/Scripts/python -m PyInstaller --noconfirm chaos_overlay.spec` → code 0 ; `dist/valorant_roulette.exe` = 56 279 498 octets. `pyi-archive_viewer -l -r` : `mlg.gif` présent à la racine, modules `chaos_overlay.*` présents.
  - `git status --short` : ni `build/` ni `dist/`.
  - README : les 11 clés du tableau = `list(REGISTRY)` dans le même ordre (comparaison python : True) ; aucun `dance.gif`, `VOTRE_NOM`, `3.13`.
- Non mesuré :
  - L'exe lancé (jamais exécuté) ; `pip install -e .[dev]` et `pyinstaller` depuis le script installé (pas fait : .venv intact) ; rendu GitHub du schéma mermaid ; affirmation README « pas d'overlay au-dessus d'un plein écran exclusif » (signalée non vérifiée dans le README).
- Écarts :
  - `keyboard==0.13.5` est encore installé dans `.venv` mais n'est plus une dépendance (plus utilisé depuis J2).
  - `addopts = "-p no:cacheprovider"` ajouté pour ne pas créer `.pytest_cache`.
  - `pillow` non déclaré : aucun import PIL dans le code.
