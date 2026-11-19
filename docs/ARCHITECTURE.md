# Architecture : Chaos Overlay v3 (2026-11-19)

La v2 (refonte du 2026-11-10, Tkinter + customtkinter, Valorant seulement) est dans l'historique git (`82a83c8`). La v3 passe à PySide6 (Qt 6) et s'ouvre à tous les FPS, choix de Malik du 2026-11-19.

## 1. Règle absolue
L'overlay est **passif**. Seules API Win32 permises : styles de NOTRE fenêtre (click-through) et raccourci clavier enregistré (`RegisterHotKey`). Interdit : lecture/écriture mémoire d'un autre processus, injection, envoi de touches ou de clics, capture d'écran, détection du jeu, tout ce qui touche un anti-triche. Un compteur d'images/s du jeu a été écarté pour cette raison (il faudrait lire ses événements de rendu).

## 2. Arborescence
```
chaos_overlay/
  __init__.py      # __version__ = "3.0.0"
  __main__.py      # python -m chaos_overlay → app.main() ; aussi le point d'entrée PyInstaller
  app.py           # ChaosApp : états (arrêt, marche, pause), minuteurs, commandes ; main()
  config.py        # Config (dataclass), load/save JSON validés champ par champ ; pur (sans Qt)
  profiles.py      # GameProfile : zones du HUD par jeu ; pur (sans Qt)
  scheduler.py     # tirage et rythme de la roulette ; pur (sans Qt)
  hotkey.py        # HOME via RegisterHotKey dans un thread, file lue par la boucle Qt
  win32.py         # make_click_through(hwnd) : seul fichier qui appelle ctypes.windll
  logs.py, paths.py, theme.py (palette + feuille de style Qt)
  malus/
    base.py        # EffectContext, Malus (render/paint, fondus), REGISTRY, @register
    15 modules, un par malus
  ui/
    overlay.py     # OverlayWindow : fenêtre transparente, liste des malus actifs, animation à la demande
    roulette.py    # Roulette (état + rythme) et paint_roulette
    dashboard.py   # Dashboard : profil, écran, fréquence, malus (case, durée, ▶ tester), état
    tray.py        # icône de la zone de notification et son menu
    icon.py        # icône dessinée en code (fenêtres, notification, .ico de l'exe)
    splash.py      # écran de démarrage
scripts/make_icon.py  # régénère assets/chaos_overlay.ico
tests/                # pytest + pytest-qt, plateforme offscreen
```

## 3. Contrats
- `EffectContext` (gelé) : `width`, `height`, `rng`, `profile` ; `scale` = hauteur / 1080, `px(v)` convertit une taille 1080p.
- `Malus` : attributs de classe `key`, `label`, `description`, `default_duration_ms`, `fade_in_ms`, `fade_out_ms`. `setup()` fait les tirages une fois ; `paint(painter, elapsed_ms)` dessine ; `render()` applique le fondu et ne dessine rien avant 0 ni après la durée. Aucune fenêtre, aucun minuteur : le rendu d'un instant est déterministe.
- `OverlayWindow` : `add_effect(malus)` ; un `QTimer` de 33 ms tourne seulement tant qu'un malus ou la roulette est visible, retire les malus finis et redessine. Drapeaux Qt : sans bordure, au premier plan, `Tool`, `WindowTransparentForInput`, `WindowDoesNotAcceptFocus` ; sous Windows, `win32.make_click_through` ajoute `WS_EX_NOACTIVATE` et vérifie les styles.
- `Roulette` : 30 noms à délais croissants (`scheduler.roulette_delays`, formule de la v1), puis le résultat 1,5 s, puis `on_done(clé)`.
- `ChaosApp` : le minuteur ne tourne qu'en marche ; la pause garde le temps restant ; « Lancer maintenant » est ignoré pendant une roulette ; « Tester » affiche un malus sans roulette ni minuteur. `after`, `clock` et `hotkey` sont injectables (tests).

## 4. Choix et compromis
- **PySide6-Essentials** plutôt que PySide6 complet : seuls QtCore, QtGui, QtWidgets sont utilisés ; la spec exclut le reste.
- **GIF lu en flux** (`GifStream` sur `QImageReader`) : une seule image décodée en mémoire, au lieu de 150 images en cache dans la v2.
- **30 i/s** et animation à la demande : fluide sans peser sur le jeu.
- **Tailles proportionnelles** à la hauteur d'écran, identiques à la v2 en 1080p.
- **Style Fusion + thème sombre** : même rendu partout, barre de titre sombre sous Windows 10/11.

## 5. Non vérifié
- Rien n'a été lancé sous Windows pour la v3 : tests, mypy et build PyInstaller ont tourné sous macOS (Qt offscreen). À vérifier sur le bureau Windows : transparence aux clics réelle, rendu par-dessus un jeu en plein écran fenêtré, HOME, icône de notification, taille de l'exe.
- Coût CPU de l'overlay translucide plein écran à 30 i/s : non mesuré.
