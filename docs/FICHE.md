# Fiche projet : Valorant Chaos Overlay (reprise, refonte du code)

Statut : validée le 2026-11-10 par l'utilisateur · Dernière modification : 2026-11-10
Une page, écrite à partir de l'existant (mode « Adapter » choisi par Malik le 2026-11-10). Rien n'est construit avant validation. Une décision produit changée après validation repasse la fiche en « brouillon ».

## 1. Pourquoi
- But : rendre le code de l'overlay propre et maintenable (modules, types, tests, config, build fiable), sans changer ce que voit le streamer. Demande de Malik : « sans lancer valo, seulement le code, faire un truc propre ».
- Pour qui : streamers et joueurs qui veulent un défi ; et Malik, qui montre le dépôt (portfolio).
- Critères de réussite :
  1. `pytest` passe sur la logique (tirage, timer, validation de config, registre des malus) sans ouvrir de fenêtre.
  2. Ajouter un malus = un nouveau fichier dans `malus/` + une ligne dans la config, sans toucher au reste.
  3. Le build PyInstaller part d'un fichier `.spec` versionné et l'exe embarque bien `mlg.gif`.
  4. Le README décrit les 11 malus réels, la vraie commande d'installation, et un schéma d'architecture.

## 2. Quoi
- Forme : application de bureau Windows (overlay plein écran transparent, click-through + Dashboard CustomTkinter). Inchangée.
- MVP (choisi par Malik le 2026-11-10) :
  - découpage en modules (un par malus, interface, configuration, cœur), annotations de type, tests de la logique sans interface ;
  - correction des bugs relevés : malus qui se chevauchent si la fréquence est courte, GIF chargé en entier au démarrage, click-through qui échoue en silence, fréquence minimale de 1 s ;
  - configuration (malus actifs, durées, fréquence) dans un fichier JSON, sauvegardée depuis le Dashboard ;
  - raccourci HOME sans mode admin (raccourci Windows enregistré au lieu du hook clavier global), sous réserve de vérification ;
  - `pyproject.toml` (cible Python 3.10+), `.gitignore`, `.spec` PyInstaller, README à jour avec schéma, licence MIT.
- Pour plus tard : nouveaux malus, captures sur le bureau (pas en jeu), CI GitHub Actions.
- Hors périmètre : lancer Valorant, captures en jeu ; toute lecture mémoire, injection, macro ou interaction avec le jeu ou Vanguard ; tout contournement d'anti-triche ; `git push` et nouvelle release sans accord.

## 3. Comment
- Techs : Python 3.10+ (la machine a 3.10.11 ; le badge « 3.13 » du README sera corrigé), Tkinter + CustomTkinter, ctypes (Win32), pytest, PyInstaller. Pourquoi : on garde la pile existante. Prix : rien de neuf à apprendre. Écarté : réécriture dans un autre framework.
- Données : un fichier de config local (JSON). Rien de sensible, rien n'est envoyé.
- Style visuel : l'actuel (palette Valorant `#0f1923`, `#ff4655`, `#ece8e1`), Dashboard inchangé.
- Contraintes : overlay strictement passif ; dépendances installées dans un `.venv` du projet après accord ; commits locaux, push sur demande.

## 4. Décisions
| Sujet | Choix | Décidé par toi le… |
|---|---|---|
| Mode de reprise | Adapter | 2026-11-10 |
| Améliorations code | Découpage + types + tests, bugs, config fichier, HOME sans admin | 2026-11-10 |
| Livraison | pyproject + .gitignore, .spec PyInstaller, README + schéma, licence | 2026-11-10 |
| mlg.gif | Gardé, chargement allégé ; README : « trouvé sur un site de GIF, source inconnue, droits non vérifiés » | 2026-11-10 |
| Licence | MIT | 2026-11-10 |
| Format de config | JSON (lisible sans dépendance) | 2026-11-10 |
| Python cible | 3.10+ | 2026-11-10 |

Changements après validation : 2026-11-10 : bouton « QUITTER » ajouté au Dashboard (il n'existait aucun moyen de quitter), décidé par Malik le 2026-11-10 (« Les deux »), en même temps que la release v2.0.0.

## 5. Suite
- Prochaine étape et coût : architecture courte écrite par moi, puis 3 jalons (J1 découpage + types + tests + bugs ; J2 config + raccourci HOME ; J3 pyproject, .spec, README, licence). Un agent exécutant par jalon, en séquence. Coût : non mesuré, ordre de grandeur quelques % de la fenêtre 5 h (repère du profil : 6 agents sonnet ≈ 4 %).
- Maquette validée : interface existante conservée telle quelle (`valorant_roulette.py`, Dashboard actuel), validée avec la fiche le 2026-11-10
- Outils vus au cadrage : questions à boutons, navigateur intégré, gh connecté (lecture seule).
- Questions encore ouvertes : `mlg.gif` vient d'un site de GIF (Tenor, Giphy…), lien inconnu : droit de redistribution non vérifié, garder / remplacer à décider avant le README (J3) ; accord pour créer le `.venv` et installer customtkinter, pytest, pyinstaller (demandé au début de J1) ; lancement de l'overlay sur le bureau pour vérifier (demandé à la fin).
