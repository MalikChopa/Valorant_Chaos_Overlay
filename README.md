# 🎯 Valorant Chaos Overlay

![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)
![Windows](https://img.shields.io/badge/OS-Windows-blue?style=for-the-badge&logo=windows)
![Vanguard](https://img.shields.io/badge/Vanguard-Safe-success?style=for-the-badge&logo=riotgames)

**Valorant Chaos Overlay** est un outil conçu pour les streamers et les joueurs cherchant un défi extrême. Il génère aléatoirement des obstructions visuelles sévères (Flashbang, Tunnel Vision, Faux Pings...) en plein match, sans jamais interagir avec la mémoire du jeu.

## ✨ Fonctionnalités

- **100% Vanguard Safe** : Le programme est un overlay passif (Click-Through absolu via l'API Win32). Il n'injecte aucun code, n'utilise pas de macros clavier, et ne modifie pas les fichiers du jeu.
- **Dashboard UI Moderne** : Interface d'administration construite avec `CustomTkinter` (Dark Mode, Thème Valorant) pour configurer les malus en temps réel.
- **Roulette Dynamique** : Animation textuelle de type "Slot Machine" in-game avant que la sentence ne tombe.
- **Système Modulaire** : Architecture orientée objet permettant d'ajouter facilement de nouveaux effets en quelques lignes de code.

## 🛠️ Les Malus Actuels

| Malus | Description de l'effet |
| :--- | :--- |
| 💥 **Flashbang** | Écran intégralement blanc pendant 2.5 secondes. |
| 🕳️ **Tunnel Vision** | Réduit le champ de vision à un simple cercle central (8s). |
| 🗺️ **HUD Blocker** | Masque stratégiquement la minimap et les munitions (12s). |
| 🎯 **Fake Crosshair** | Affiche un faux viseur vert géant légèrement décalé du centre (10s). |
| ⚠️ **Paranoia** | Fait apparaître de faux pings de danger autour du viseur. |
| 🪟 **Screen Crack** | Simule une fracture de l'écran obstruant la visibilité. |
| 🦟 **Mosquito** | Un pixel mort géant rebondit de façon erratique sur l'écran. |
| 💻 **Fake Crash** | Faux écran bleu fatal (Vanguard Disconnected) pour provoquer la panique. |
| 💃 **Dance GIF** | Distraction visuelle lourde au centre de l'écran. |

## 🚀 Installation & Exécution

### Option 1 : Télécharger l'exécutable (Recommandé)
1. Allez dans l'onglet **Releases** et téléchargez `valorant_roulette.exe`.
2. Lancez Valorant et réglez le mode d'affichage sur **Plein Écran Fenêtré (Borderless Windowed)**.
3. Exécutez le `.exe` en **mode Administrateur** (Requis pour l'écoute globale du clavier).
4. Appuyez sur la touche `Home` (`Origine`) en jeu pour ouvrir le Dashboard et configurer votre partie.

### Option 2 : Compiler depuis la source
Prérequis : Python 3.10+
```bash
# 1. Cloner le repository
git clone [https://github.com/VOTRE_NOM/valorant_chaos_overlay.git](https://github.com/VOTRE_NOM/valorant_chaos_overlay.git)
cd valorant_chaos_overlay

# 2. Installer les dépendances
pip install customtkinter keyboard pyinstaller

# 3. Compiler l'exécutable (intègre l'image dance.gif en mémoire)
pyinstaller --noconsole --onefile --add-data "dance.gif;." valorant_roulette.py
