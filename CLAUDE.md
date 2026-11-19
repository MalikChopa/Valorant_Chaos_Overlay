# Chaos Overlay (ex-Valorant Chaos Overlay)

But : overlay passif pour streamers de FPS (malus visuels aléatoires par-dessus le jeu). v3 : PySide6, tous les FPS. Taille : moyenne (une douzaine de fichiers). Flux : logiciel (reprise sans cadrage, mode « Adapter »).
Fiche : v2 validée le 2026-11-10 (`docs/FICHE.md`) ; v3 décidée le 2026-11-19 (voir Décisions et `docs/ARCHITECTURE.md`).
Langue de travail : français, tutoiement, réponses courtes.

## Machine ou cibles (relevé du 2026-11-10)
- Cible : Windows 10/11, Python 3.10+. Machine de dev : Windows 11, Python 3.10.11, git, gh.
- 2026-11-19 : la v3 a été écrite et testée sous macOS (Qt offscreen) ; pas encore lancée sous Windows.

## Contraintes
- Overlay strictement passif : aucune lecture mémoire, injection, macro, ni interaction avec le jeu ou son anti-triche (Vanguard, VAC, EAC...). Ne contourner aucun anti-triche ; une idée qui s'en approche est écartée et signalée.
- Ne jamais lancer Valorant, aucune capture en jeu. L'overlay peut être lancé sur le bureau seulement avec l'accord de Malik.
- Dépendances : uniquement dans `.venv` du projet, après accord sur la liste.
- Git : commits locaux, un par étape vérifiée ; push et release seulement sur demande.

## Contenu du dossier
- `chaos_overlay/` : le code (voir `docs/ARCHITECTURE.md`). `mlg.gif` : média du malus GIF (compressé le 2026-11-19 à 8,8 Mo, commit 82a83c8 ; ne plus le modifier).
- `docs/FICHE.md`, `docs/HANDOFF.md`, `docs/JOURNAL.md`, `docs/briefs/` : historique de la refonte v2 (2026-11-10).

## Décisions (datées)
- 2026-11-10 : reprise en mode « Adapter » (utilisateur).
- 2026-11-10 : améliorations retenues : découpage + types + tests, bugs, config en fichier, HOME sans admin, pyproject + .gitignore, .spec PyInstaller, README + schéma, licence ; mlg.gif gardé avec source citée (utilisateur).
- 2026-11-10 : mlg.gif gardé, droits non vérifiés (source : site de GIF, lien inconnu), le README le dira (utilisateur).
- 2026-11-10 : J1 fait (paquet `chaos_overlay/`) ; `valorant_roulette.py` n'est plus qu'un lanceur (délégué).
- 2026-11-10 : journal dans un fichier `chaos_overlay.log` à côté de l'exe (rotation 256 Ko), car l'exe sans console masquait les avertissements (délégué).
- 2026-11-10 : bornes de config : fréquence 1 à 3600 s, durées 500 à 60 000 ms ; config `chaos_config.json` à côté de l'exe (délégué).
- 2026-11-19 : « FPS overlay » = tous les jeux FPS, via des profils de jeu choisis à la main ; pas de compteur d'images/s (il faudrait lire le jeu) (Malik).
- 2026-11-19 : passage de tkinter/customtkinter à PySide6 (Malik).
- 2026-11-19 : nom « Chaos Overlay » ; dépôt à renommer `chaos-overlay` seulement après fusion et accord (Malik).
- 2026-11-19 : malus : les 11 rendus génériques + 4 nouveaux (lunette de sniper, PV critiques, faux kill feed, viseur ivre) (Malik).
- 2026-11-19 : « moderne et bien intégré » : icône de notification (pause, malus maintenant, quitter), bouton Tester, compte à rebours, thème sombre, icône d'exe (Malik, interprété par la session).

## Règles du projet
- Méthode « Diapason » : la session principale pilote, délègue, vérifie. Un agent = une tâche = ses fichiers ; jamais deux rédacteurs sur les mêmes fichiers.
- Ne jamais annoncer fini ce qui n'est pas mesuré ou sourcé.
- Toujours demander avant : argent, installations, gros téléchargements, publication (push, release), envoi de messages, comptes, suppressions.
- Ne jamais : contourner une protection, copier une œuvre protégée, mettre un secret dans le projet, modifier les originaux (`mlg.gif`).
- Palette conservée : `#0f1923`, `#1f2326`, `#ff4655`, `#ece8e1`, `#8b978f`, `#535c65`.
- Pile : Python 3.10+, PySide6-Essentials, pytest + pytest-qt (offscreen), mypy strict, PyInstaller.
- Quota : géré par Diapason seulement (seuils 70/80/90 %).
