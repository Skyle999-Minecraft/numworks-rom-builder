# NumWorks ROM Builder

**Le but : mettre plusieurs de vos jeux NES ou Game Boy / Game Boy Color sur
une NumWorks, puis choisir le jeu depuis un menu sur la calculatrice, sans
refaire une installation pour chaque jeu.**

ROM Builder est l'application graphique qui prepare tout sur le PC. L'emulateur
modifie est l'application qui execute les jeux sur la calculatrice. Il faut les
deux : ROM Builder seul ne permet pas de jouer.

## Exemple concret

Vous avez trois jeux Game Boy/Color obtenus legalement :

1. Sur Windows, ouvrir ROM Builder et choisir **Game Boy / Game Boy Color**.
2. Ajouter les trois fichiers `.gb` / `.gbc` et choisir un dossier de sortie.
3. Cliquer sur **Preparer / compiler** : l'outil verifie les ROMs, les regroupe
   dans `roms.gb`, puis compile l'application modifiee `peanutgb.nwa`.
4. Sur https://my.numworks.com/apps, installer `peanutgb.nwa` en lui associant
   `roms.gb` comme donnees externes. L'envoi USB reste une operation manuelle.
5. Sur la calculatrice, ouvrir l'application Game Boy : un menu liste les trois
   jeux ; choisir l'un d'eux avec les fleches et valider pour le lancer.

Pour la NES, c'est le meme principe avec des fichiers `.nes` et le couple
`nofrendo.nwa` + `roms.nes`.

```text
PC : vos ROMs individuelles
            |
      ROM Builder + sources de l'emulateur modifie
            |
      application .nwa + fichier regroupant les jeux
            |
      installation manuelle sur la NumWorks
            |
Calculatrice : menu de choix du jeu -> execution du jeu
```

Les jeux restent separes dans le fichier : « fusionner » signifie ici les
**regrouper**, pas melanger leur code ou convertir une console en une autre.
Le conteneur peut contenir jusqu'a 64 jeux d'une meme famille, sous reserve de
la place disponible. Il faut deux applications distinctes pour NES et Game Boy.
Avec une seule ROM, le jeu se lance directement, sans menu.

## Ce qui est disponible aujourd'hui

- **Publie ici :** l'interface Windows, son moteur de preparation et ses tests.
- **Fonctionne dans l'environnement local complet :** preparation des ROMs et
  compilation avec les deux portages modifies presents sur le PC.
- **Pas encore distribue :** les sources et binaires des portages modifies,
  dans l'attente de clarification de leurs licences. Telecharger ce depot seul
  ne fournit donc pas encore tout le necessaire pour suivre l'exemple ci-dessus.
- **Aucun jeu fourni.** Les essais PC ne garantissent pas la compatibilite de
  chaque jeu ; le rendu et les performances Color restent a verifier sur materiel.

Sur Game Boy, Accueil revient au menu s'il y a plusieurs jeux. Sur NES, quitter
le jeu ferme l'application : la relancer permet d'en choisir un autre.
Le portage Game Boy ne fournit ni son ni sauvegarde persistante.

**Attention :** une installation d'applications externes remplace les autres.
Selectionner en une seule operation tous les `.nwa` que vous souhaitez conserver.

**Important :** les conteneurs doivent etre utilises avec les **emulateurs modifies**,
pas avec leurs versions d'origine. L'outil regroupe les ROMs sans fusionner leur code.
Voir le [guide multi-ROMs et installation](MULTI-ROMS.md) et le
[resultat detaille de la verification des licences](LICENSE-REVIEW.md).

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
