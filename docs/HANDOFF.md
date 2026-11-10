# Handoff : Valorant Chaos Overlay (2026-11-10)

Dernière visite : 2026-11-10
Jalon : cadrage, fiche en brouillon
Fiche : brouillon · Maquette : pas encore

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
- Installé, acheté, publié : rien.

## Agents lancés
| Agent | Tâche | Modèle | Fichier de travail | Statut | Brief | Coût |
|---|---|---|---|---|---|---|

## Pistes échouées et pièges connus (ne jamais couper)
- Le README parle de `dance.gif` ; le bon fichier est `mlg.gif`.

## Décisions et pistes abandonnées
- 2026-11-10 : mode « Adapter » ; liste d'améliorations choisie (voir CLAUDE.md).

## Reprise immédiate (dans l'ordre)
1. Faire valider `docs/FICHE.md` (Valider et continuer / Modifier / Tout revoir) et obtenir la source de mlg.gif.
2. Après validation : lire le quota, écrire `docs/ARCHITECTURE.md`, demander l'accord pour le `.venv`, lancer J1.

## En attente de Malik
- Validation de la fiche ; source et licence de mlg.gif.

## Coûts mesurés
- aucun agent lancé.

## Ce qui ne se transmet pas
Historique de conversation, agents en cours, mémoire personnelle, liens d'artifacts privés, comptes externes : seuls les fichiers du projet comptent.
