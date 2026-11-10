# Architecture : Valorant Chaos Overlay (refonte 2026-11-10)

Référence : `docs/FICHE.md` (validée le 2026-11-10). Point de départ : `valorant_roulette.py` (commit a74abcb). Ce que voit le streamer ne change pas : mêmes couleurs, textes, tailles, durées et timings que le code actuel, sauf les corrections listées en §4.

## 1. Règle absolue
L'overlay est **passif**. Seules API Win32 permises : styles de fenêtre (click-through) et raccourci clavier enregistré (`RegisterHotKey`). Interdit : lecture/écriture mémoire d'un autre processus, injection, envoi de touches ou de clics, capture d'écran du jeu, détection du jeu, tout ce qui touche Vanguard.

## 2. Arborescence cible
```
chaos_overlay/
  __init__.py          # __version__ = "2.0.0"
  __main__.py          # python -m chaos_overlay → app.main()
  app.py               # main() : NullWriter, crash_log, création Tk, assemblage
  paths.py             # app_dir() (dossier de l'exe ou du projet), resource_path() (_MEIPASS) : sans chdir
  theme.py             # palette et polices (constantes reprises du code actuel)
  scheduler.py         # logique pure : tirage, séquence de la roulette, validation de fréquence
  config.py            # (J2) dataclass Config, load/save JSON, validation ; pure
  hotkey.py            # (J2) RegisterHotKey dans un thread dédié + file d'attente lue par root.after
  win32.py             # make_click_through(hwnd) -> bool ; seul fichier qui appelle ctypes.windll
  malus/
    __init__.py        # REGISTRY : dict[str, type[Malus]], décorateur @register ; importe tous les malus
    base.py            # Malus (ABC) + EffectContext
    flashbang.py tunnel_vision.py hud_blocker.py fake_crosshair.py scanlines.py
    mlg_gif.py fake_crash.py blind_spot.py paranoia.py screen_crack.py mosquito.py
  ui/
    overlay.py         # fenêtre transparente plein écran + Canvas, fournit l'EffectContext
    splash.py          # écran de chargement
    dashboard.py       # Dashboard CustomTkinter (identique visuellement)
    roulette.py        # affichage de la roulette, piloté par scheduler.roulette_delays()
valorant_roulette.py   # garde ce nom (releases existantes) : 3 lignes qui appellent chaos_overlay.app.main()
tests/                 # pytest, sans fenêtre
```
Noms de malus (clés) inchangés : `flashbang, tunnel_vision, hud_blocker, fake_crosshair, scanlines, mlg_fullscreen, fake_crash, blind_spot, paranoia, screen_crack, mosquito` (ordre d'affichage conservé).

## 3. Contrats
- `EffectContext` (dataclass) : `canvas`, `width`, `height`, `after(ms, fn) -> str`, `after_cancel(id)`, `rng: random.Random`.
- `Malus` : attributs de classe `key: str`, `default_duration_ms: int`. Méthodes : `start(ctx)`, `stop()`. Chaque **instance** garde ses propres éléments de canvas et ids `after` ; `stop()` les supprime tous et est idempotente. Une instance par déclenchement.
- `scheduler` (aucun import tkinter) :
  - `pick(active: Sequence[str], rng) -> str` (renvoie `"rien"` si vide, comme aujourd'hui) ;
  - `roulette_delays(spins=30, start_delay=50) -> list[int]` reproduit exactement la formule actuelle (`new_delay = delay + int(120 / spins_left)`) ;
  - `parse_frequency(text) -> int | None` (entier ≥ 1, sinon None).
- Les modules hors `ui/`, `win32.py`, `hotkey.py`, `app.py` s'importent sans display et sans effet de bord (pas de `os.chdir`, pas de remplacement de stdout à l'import).
- Typage : annotations partout ; `mypy --strict chaos_overlay` sans erreur (`ignore_missing_imports` pour customtkinter seulement).

## 4. Corrections de bugs (J1)
1. **Chevauchement** : l'état mutable partagé (`self.mosq_*`, `self.is_animating`, `self.gif_canvas_obj`) disparaît, l'état vit dans l'instance du malus. Cadence inchangée (le minuteur repart dès que le malus démarre, comme aujourd'hui) : deux malus peuvent donc se superposer, mais chacun se nettoie seul.
2. **GIF** : le chargement se fait au premier déclenchement, plus au démarrage, et seulement pour les images affichées pendant la durée de l'effet (ceil(6000 / 40) = 150 images au lieu d'environ 608). Le délai de 40 ms est conservé. `mlg.gif` absent : le malus ne fait rien, comme aujourd'hui, et le journal le note.
3. **Click-through** : `make_click_through` renvoie un booléen. En cas d'échec, un avertissement s'affiche (messagebox), car l'overlay bloquerait les clics.
4. **Effets de bord à l'import** déplacés dans `main()`. `crash_log.txt` est écrit dans `app_dir()`.

## 5. Jalons
- **J1, cœur (opus)** : arborescence §2 sans `config.py` ni `hotkey.py` ; la lib `keyboard` reste pour HOME. Bugs de §4. Tests : `pick` (rng à graine), `roulette_delays` (égalité avec la formule d'origine, 30 valeurs), `parse_frequency`, registre (11 clés, ordre, `default_duration_ms` égal aux durées actuelles : 2500, 8000, 12000, 10000, 10000, 6000, 2500, 8000, 4000, 8000, 10000), import de `chaos_overlay.malus` sans display, `stop()` idempotent avec un faux canvas. Critères : `pytest` vert, `mypy --strict` vert, `python -c "import chaos_overlay.malus"` sans erreur.
- **J2, config + HOME (opus)** : `config.py` (JSON `chaos_config.json` dans `app_dir()`, champs : `frequency_s`, `enabled{key: bool}`, `durations_ms{key: int}`, `hotkey="home"` ; un fichier absent ou invalide donne les valeurs par défaut et un avertissement journalisé, sans crash ; une clé inconnue est ignorée). Le Dashboard enregistre au clic « Démarrer ». `hotkey.py` : `RegisterHotKey(None, id, 0, VK_HOME)` dans un thread avec sa propre boucle `GetMessageW`, le signal passe par une `queue.Queue` lue toutes les 100 ms par `root.after`. Échec de l'enregistrement (touche déjà prise) : avertissement. La lib `keyboard` est retirée. Tests : config (aller-retour, fichier corrompu, valeurs hors bornes, clé inconnue).
- **J3, livraison (sonnet)** : `pyproject.toml` (Python ≥ 3.10, dépendances aux versions figées), `.gitignore`, `chaos_overlay.spec` (embarque `mlg.gif`), `LICENSE` (MIT, 2026, Malik), README (11 malus, installation venv, build, schéma mermaid, section « Ce que l'overlay ne fait pas », mention honnête sur Vanguard). Statut de `mlg.gif` selon la décision de Malik.

## 6. Non vérifié
- `RegisterHotKey` quand la fenêtre au premier plan tourne en administrateur (UIPI) : non vérifié à la source. À tester sur le bureau avec une fenêtre lancée en admin, avec l'accord de Malik. Le jeu ne sera jamais lancé.
- Gain de mémoire du GIF : estimation (environ 4 fois moins d'images), à mesurer au lancement sur le bureau.
