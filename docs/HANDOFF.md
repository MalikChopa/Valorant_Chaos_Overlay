# Handoff : Valorant Chaos Overlay (2026-11-10)

Dernière visite : 2026-11-10
Jalon : v2.0.0 publiée (bouton Quitter inclus), 2026-11-10
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
- [V 2026-11-10] Lancé sur le bureau avec l'accord de Malik (`python -m chaos_overlay`, sans le jeu) : fenêtre « Chaos Overlay - Core » qui répond, 51,6 Mo de RAM au démarrage (Get-Process, avant tout tirage du GIF) ; Malik confirme « ça marche ». Processus arrêté ensuite par Diapason. Non mesuré : HOME avec une fenêtre admin au premier plan, RAM après le malus GIF.
- [V 2026-11-10] Bouton Quitter : pytest 312 passed, essai réel (sortie en 4,0 s, HOME libérée). Exe reconstruit (56 280 908 octets, sha256 3db88059…), lancé 6 s sur le bureau : fenêtre « Chaos Overlay - Core », 50,8 Mo, puis fermé. Piège : l'exe onefile crée un 2e processus, fermer les deux.
- Installé, acheté, publié : `.venv` du projet (accord de Malik le 2026-11-10) : customtkinter 6.0.0, keyboard 0.13.5, pytest 9.2.0, mypy 2.4.1, pyinstaller 6.22.3 ; 95 Mo mesurés (`du -sh`), annoncés « quelques dizaines ». Poussé sur origin/main le 2026-11-10 (a74abcb..b893328), avec l accord de Malik.

## Agents lancés
| Agent | Tâche | Modèle | Fichier de travail | Statut | Brief | Coût |
|---|---|---|---|---|---|---|
| exec-J1 | J1 cœur : découpage, types, tests, bugs | opus | docs/JOURNAL.md §J1 | terminé (vérifié, commit 732e4f6) | `docs/briefs/01-executant-J1.md` | 98,5 k tokens · 10 min |
| exec-J2 | J2 config JSON, HOME sans admin, journal fichier | opus | docs/JOURNAL.md §J2 | terminé (vérifié) | `docs/briefs/02-executant-J2.md` | 78 k tokens · 8 min |
| exec-J3 | J3 pyproject, .gitignore, .spec, licence, README | sonnet | docs/JOURNAL.md §J3 | terminé (vérifié) | `docs/briefs/03-executant-J3.md` | 33 k tokens · 1,5 min |

## Pistes échouées et pièges connus (ne jamais couper)
- L'exe onefile lance un processus enfant : arrêter le parent ne ferme pas la fenêtre.
- Le README parle de `dance.gif` ; le bon fichier est `mlg.gif`.

## Décisions et pistes abandonnées
- 2026-11-10 : mode « Adapter » ; liste d'améliorations choisie (voir CLAUDE.md).
- 2026-11-10 : mlg.gif gardé par Malik, droits non vérifiés ; le README (J3) le dira : « trouvé sur un site de GIF, source inconnue ».

## Reprise immédiate (dans l'ordre)
1. J1 à J3 faits et vérifiés (commits locaux). Attendre les réponses de Malik ci-dessous.

## En attente de Malik
- keyboard 0.13.5 reste dans .venv sans être utilisé : le désinstaller ? (petit, local)

## Coûts mesurés
- aucun agent lancé.

## Ce qui ne se transmet pas
Historique de conversation, agents en cours, mémoire personnelle, liens d'artifacts privés, comptes externes : seuls les fichiers du projet comptent.
