# Handoff : Valorant Chaos Overlay (2026-11-10)

Dernière visite : 2026-11-10
Jalon : J1 (cœur) en cours
Fiche : validée le 2026-11-10 · Maquette : interface existante conservée

Ordre de lecture : `CLAUDE.md`, ce fichier, `docs/FICHE.md`.

## Reprise
- Avec le skill : `/diapason C:\Users\Abdel-Malik\Projects\Valorant_Chaos_Overlay`.
- Sans le skill : « Tu es Diapason de ce projet. Lis CLAUDE.md puis docs/HANDOFF.md. Tu pilotes, tu délègues chaque tâche à un agent du bon modèle, tu vérifies toi-même avant de dire que c'est fini, et tu rends compte brièvement. Commence par "Reprise immédiate". »

Git : a74abcb (avant tout changement). Plafond : 8 Ko.

## Demandes de Malik (mot pour mot)
- « améliorer le projet dans un sous-chat » (2026-11-10)
- « sans lancer valo, seulement le code, faire un truc propre » (2026-11-10)

## État
- [V 2026-11-10] État des lieux en lecture seule (lecture de README.md et valorant_roulette.py, en-tête de mlg.gif, `gh release list`) : 1 fichier Python de 372 lignes, 11 malus, releases v1.0.0 et v1.1.0, pas de licence.
- [V 2026-11-10] README : commande PyInstaller avec `dance.gif` alors que le code charge `mlg.gif` (lu ligne 49 du README et ligne 42 du code).
- [V 2026-11-10] `python --version` → 3.10.11 ; `import customtkinter` → ModuleNotFoundError.
- [V 2026-11-10] mlg.gif : GIF89a 640×360, environ 608 images (comptage des blocs de contrôle graphique), 45 Mo.
- [?] Mémoire du GIF chargé en entier ≈ 560 Mo : estimation, non mesurée.
- [V 2026-11-10] Fiche validée par Malik, architecture écrite (`docs/ARCHITECTURE.md`), commit d564d74.
- Installé, acheté, publié : `.venv` du projet (accord de Malik le 2026-11-10) : customtkinter 6.0.0, keyboard 0.13.5, pytest 9.2.0, mypy 2.4.1, pyinstaller 6.22.3 ; 95 Mo mesurés (`du -sh`), annoncés « quelques dizaines ». Rien de publié.

## Agents lancés
| Agent | Tâche | Modèle | Fichier de travail | Statut | Brief | Coût |
|---|---|---|---|---|---|---|
| exec-J1 | J1 cœur : découpage, types, tests, bugs | opus | docs/JOURNAL.md §J1 | en cours | `docs/briefs/01-executant-J1.md` | non mesuré (fenêtre 5 h à 32 % au lancement) |

## Pistes échouées et pièges connus (ne jamais couper)
- Le README parle de `dance.gif` ; le bon fichier est `mlg.gif`.

## Décisions et pistes abandonnées
- 2026-11-10 : mode « Adapter » ; liste d'améliorations choisie (voir CLAUDE.md).
- 2026-11-10 : mlg.gif gardé par Malik, droits non vérifiés ; le README (J3) le dira : « trouvé sur un site de GIF, source inconnue ».

## Reprise immédiate (dans l'ordre)
1. Si exec-J1 « en cours » sans rapport : vérifier `docs/JOURNAL.md` §J1 et `git status`, puis relancer avec `briefs/continuation`.
2. Vérifier J1 soi-même (pytest, mypy, imports), commiter, puis brief J2 (opus).

## En attente de Malik
- Accord pour lancer l'overlay sur le bureau (vérification visuelle, test de RegisterHotKey), plus tard.

## Coûts mesurés
- aucun agent lancé.

## Ce qui ne se transmet pas
Historique de conversation, agents en cours, mémoire personnelle, liens d'artifacts privés, comptes externes : seuls les fichiers du projet comptent.
