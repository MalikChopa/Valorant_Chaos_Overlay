# Valorant Chaos Overlay

But : overlay passif pour streamers (malus visuels aléatoires par-dessus le jeu) ; reprise pour rendre le code propre. Taille : moyenne (une douzaine de fichiers). Flux : logiciel (reprise sans cadrage, mode « Adapter »).
Fiche : brouillon (`docs/FICHE.md`). Maquette : pas encore (proposé : interface existante conservée).
Langue de travail : français, tutoiement, réponses courtes.

## Machine ou cibles (relevé du 2026-11-10)
- Cible : Windows 10/11, Python 3.10+. Machine de dev : Windows 11, Python 3.10.11, git, gh. customtkinter non installé.

## Contraintes
- Overlay strictement passif : aucune lecture mémoire, injection, macro, ni interaction avec le jeu ou Vanguard. Ne contourner aucun anti-triche ; une idée qui s'en approche est écartée et signalée.
- Ne jamais lancer Valorant, aucune capture en jeu. L'overlay peut être lancé sur le bureau seulement avec l'accord de Malik.
- Dépendances : uniquement dans `.venv` du projet, après accord sur la liste.
- Git : commits locaux, un par étape vérifiée ; push et release seulement sur demande.

## Contenu du dossier
- `docs/HANDOFF.md` : état, agents lancés, reprise. **À lire en premier.**
- `docs/FICHE.md` : la fiche (référence ; pas de code avant validation).
- `docs/briefs/` : consignes envoyées aux agents.
- `valorant_roulette.py` : code actuel (un seul fichier, avant découpage). `mlg.gif` : média du malus GIF (original, ne pas modifier).

## Décisions (datées)
- 2026-11-10 : reprise en mode « Adapter » (utilisateur).
- 2026-11-10 : améliorations retenues : découpage + types + tests, bugs, config en fichier, HOME sans admin, pyproject + .gitignore, .spec PyInstaller, README + schéma, licence ; mlg.gif gardé avec source citée (utilisateur).
- 2026-11-10 : mlg.gif gardé, droits non vérifiés (source : site de GIF, lien inconnu), le README le dira (utilisateur).
- 2026-11-10 : J1 fait (paquet `chaos_overlay/`) ; `valorant_roulette.py` n'est plus qu'un lanceur (délégué).
- 2026-11-10 : journal dans un fichier `chaos_overlay.log` à côté de l'exe (rotation 256 Ko), car l'exe sans console masquait les avertissements (délégué).
- 2026-11-10 : bornes de config : fréquence 1 à 3600 s, durées 500 à 60 000 ms ; config `chaos_config.json` à côté de l'exe (délégué).

## Règles du projet
- Méthode « Diapason » : la session principale pilote, délègue, vérifie. Un agent = une tâche = ses fichiers ; jamais deux rédacteurs sur les mêmes fichiers.
- Ne jamais annoncer fini ce qui n'est pas mesuré ou sourcé.
- Toujours demander avant : argent, installations, gros téléchargements, publication (push, release), envoi de messages, comptes, suppressions.
- Ne jamais : contourner une protection, copier une œuvre protégée, mettre un secret dans le projet, modifier les originaux (`mlg.gif`).
- Palette conservée : `#0f1923`, `#1f2326`, `#ff4655`, `#ece8e1`, `#8b978f`, `#535c65`.
- Quota : géré par Diapason seulement (seuils 70/80/90 %).
