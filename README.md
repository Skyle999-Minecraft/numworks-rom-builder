# NumWorks ROM Builder

Interface graphique Windows en Python/tkinter pour selectionner des ROMs NES
ou Game Boy / Game Boy Color, preparer un conteneur multi-jeux et compiler
l'emulateur correspondant. Aucun jeu ni emulateur n'est distribue ici.

## Installation et dependances externes

- Python 3.10+ avec tkinter.
- Arm GNU Toolchain et Node.js/npm/npx pour compiler les applications.
- Les dossiers `nofrendo/` et `peanutgb/` doivent etre places a la racine de
  ce depot, a cote de `rom-builder/`.
- **Il faut les versions modifiees compatibles** : scripts `pack_roms.py`,
  `check_pack.py`, et `build.py` acceptant `--output` et `-d`, format NWROMS v1.
  Les versions amont seules ne garantissent pas cette interface.

**Limite de cette publication :** les portages modifies ne sont pas inclus,
leurs licences globales devant encore etre clarifiees. Ce depot fournit donc
l'interface et ses tests, pas une installation autonome prete a compiler.
Les tests d'integration dependent aussi des projets compatibles et de leurs
ROMs de demonstration obtenues separement avec les droits necessaires.

Double-cliquer sur `Compiler-ROMs.cmd` une fois ces dependances disponibles.
Les preferences sont locales, les sorties sont creees dans de nouveaux dossiers,
et aucune installation USB n'est lancee automatiquement.

## Projets tiers utilises, non republies

- Nofrendo pour NumWorks : https://codeberg.org/Yaya-Cout/nofrendo
- Portage PeanutGB pour NumWorks : https://github.com/nwagyu/peanutgb
- Coeur Peanut-GB : https://github.com/deltabeard/Peanut-GB
- Coeur Color pico-peanutGB : https://github.com/PicoPlus-devel/pico-peanutGB
- Outils NumWorks/nwlink : https://www.npmjs.com/package/nwlink

La licence MIT du coeur Peanut-GB ne permet pas de deduire automatiquement
la licence de tout le portage. Aucun de ces projets n'est revendique comme
une creation du contributeur ou de l'IA.

## Verification

Avant publication : 20 tests locaux passes, dont les tests Tk et de preferences,
et compilation Game Boy avec les projets compatibles presents localement.
Verification publique sans emulateur :

```sh
python -B -m unittest discover -s rom-builder -p test_settings.py -v
```

Voir [le guide de l'interface](rom-builder/README.md) pour les fonctions et les tests.

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
