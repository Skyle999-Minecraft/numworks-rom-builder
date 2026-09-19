**Publication partielle :** les emulateurs modifies ne sont pas inclus.
Lire les prerequis et limites du [README principal](../README.md).

# NumWorks ROM Builder

Application Windows en Python/tkinter, sans bibliotheque graphique a installer.
Conserver ce dossier a cote des projets `nofrendo` et `peanutgb`.

## Utilisation

1. Double-cliquer sur `Compiler-ROMs.cmd` a la racine du dossier NumWorks.
2. Choisir **NES** ou **Game Boy / Game Boy Color**.
3. Ajouter ses ROMs individuelles : `.nes`, ou `.gb` / `.gbc` (pas de ZIP).
4. Choisir un dossier de sortie existant.
5. Cliquer sur **Preparer / compiler** et suivre le journal.
6. Cliquer sur **Ouvrir le resultat**.

Chaque console conserve sa propre liste entre les sessions. Maximum 64 jeux.
Les jeux sont classes par nom par les outils existants ; le nom affiche sur
calculatrice est limite a 24 caracteres. Deux noms affiches identiques sont
refuses par la verification. Une ROM refusee interrompt toute la preparation :
elle n'est jamais silencieusement omise du resultat.

### Fonctions pratiques

- **Ajouter un dossier** importe ses ROMs compatibles (sans parcourir les sous-dossiers).
- Les fichiers deplaces ou supprimes apparaissent en rouge avec la mention **Absent**.
- Le nombre de ROMs et leur taille totale sont affiches (hors taille de l'emulateur).
- **Verifier les outils** detecte ARM, Node.js et npx sans telecharger ni installer.
  Cette verification est aussi faite avant toute compilation ; le mode conteneur seul
  n'en a pas besoin. La detection ne garantit pas la disponibilite du reseau ou de nwlink.
- Le journal colore les etapes et erreurs ; on peut desactiver son defilement et
  **enregistrer le journal**, y compris apres un echec. Un compteur indique le temps ecoule.
- La liste des jeux et le journal ont chacun leur onglet pour garder les commandes
  visibles. Le journal s'ouvre automatiquement au lancement d'une preparation.
- Raccourcis : **Ctrl+O** ajouter, **Ctrl+Entree** lancer, **Ctrl+A** tout selectionner
  dans la liste, **Suppr** retirer la selection.

La console, les listes, le dossier de sortie, l'option de compilation et le dernier
resultat sont memorises localement dans `%LOCALAPPDATA%\NumWorksRomBuilder\settings.json`
sur Windows (sinon `~/.config/NumWorksRomBuilder/settings.json`). Seuls les chemins sont
enregistres, jamais le contenu des ROMs. Un fichier de preferences invalide est ignore.
Supprimer ce fichier pour reinitialiser les preferences. Aucun envoi de ces donnees.

Les ROMs sont regroupees, pas converties : l'application compile l'emulateur
qui les execute. Un seul jeu demarre directement ; plusieurs donnent un menu.

## Resultat

Un **nouveau sous-dossier unique** contient :

- NES : `nofrendo.nwa` et `roms.nes` ;
- Game Boy / Color : `peanutgb.nwa` et `roms.gb` (meme pour des jeux `.gbc`) ;
- `LISEZMOI.txt` et `compilation.log`.

Decocher **Compiler aussi l'application .nwa** pour produire uniquement le
conteneur de ROMs, sans toolchain ARM ni Node.js. Il faut alors deja disposer
d'une version compatible de l'emulateur multi-ROMs.

La compilation se fait dans un dossier temporaire. Les sources, ROMs originales,
anciens resultats et binaires du dossier `a-installer` ne sont pas remplaces.
En cas d'echec, aucun resultat partiel n'est publie ; l'erreur reste dans le journal.
La fenetre reste reactive, mais il faut attendre la fin avant de la fermer.

## Prerequis

- Python **3.10+** avec tkinter (inclus dans l'installation Windows standard).
- Pour compiler : Arm GNU Toolchain et Node.js avec `npx`, comme les scripts existants.
  Le compilateur ARM est aussi recherche dans ses dossiers d'installation Windows.
- `nwlink` **0.0.19** est utilise via `npx` ; Internet peut etre necessaire au premier lancement.

Aucune installation USB automatique. Le bouton du site ouvre
https://my.numworks.com/apps : installer remplace les autres applications,
donc envoyer tous les `.nwa` a conserver ensemble, avec leurs donnees externes.
Le mode Color reste a verifier sur calculatrice ; pas de son ni de sauvegardes
persistantes pour Game Boy. Utiliser uniquement des ROMs obtenues legalement.

## Tests

Depuis ce dossier : `python -B -m unittest -v test_builder test_settings test_gui`.
Les tests utilisent les ROMs de demonstration presentes dans les projets et
des dossiers temporaires. `python -B test_gui.py` verifie aussi la fenetre Tk
et la preparation asynchrone, sans lancer la compilation ARM.

## Transparence : assistance de l'IA

Ce projet contient du code, des modifications, des tests et de la documentation
realises avec l'assistance de ChatGPT (OpenAI). Cette assistance ne constitue
pas une garantie de correction ou de securite. Les limites et verifications
effectuees sont documentees ; une compilation reussie ne remplace pas un essai
sur calculatrice.

Cette publication est un instantane nettoye, avec un historique Git neuf et une
identite de commit neutre pour proteger la vie privee du contributeur. Les
historiques locaux, chemins personnels, preferences, journaux, ROMs et binaires
precompiles ne sont pas publies. Aucune cle API n'est necessaire pour executer
ces projets : les outils n'appellent aucun service d'IA.

## Droits et credits

Aucune nouvelle licence de redistribution n'est accordee par cet instantane.
Le caractere public du depot ne constitue pas a lui seul une licence libre.
Les marques Windows, Nintendo et NumWorks appartiennent a leurs proprietaires
respectifs ; ces projets ne sont pas des produits officiels de ces entreprises.
Les eventuelles notices de tiers presentes dans les fichiers restent applicables.
