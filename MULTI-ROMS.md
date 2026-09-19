# ROM Builder et les emulateurs modifies : ce qu'il faut installer

## Pourquoi les versions d'origine ne suffisent pas

L'outil ne fusionne pas le code des jeux et ne convertit pas une console en une
autre. Il **regroupe plusieurs ROMs individuelles dans un conteneur NWROMS v1**,
avec un index pour que l'emulateur modifie puisse choisir le jeu a executer.
Un emulateur d'origine prevu pour une ROM brute ne sait pas lire cet index.
Ne pas utiliser le conteneur comme une ROM brute dans un autre emulateur.

| Console choisie | Application modifiee requise | Donnees externes generees |
| --- | --- | --- |
| NES | `nofrendo.nwa`, version multi-ROMs | `roms.nes` |
| Game Boy / Game Boy Color | `peanutgb.nwa`, version multi-ROMs avec Color | `roms.gb` |

L'extension du conteneur Color reste `.gb`, meme si ses jeux sources sont `.gbc`.
Une seule ROM se lance directement ; plusieurs affichent le menu de selection.

## Sur le PC

1. Disposer legalement des ROMs individuelles `.nes`, `.gb` ou `.gbc`.
2. Disposer des **sources modifiees compatibles** des portages, a cote du
   dossier `rom-builder/`, dans `nofrendo/` et `peanutgb/`.
3. Installer Python/tkinter, et ARM GNU Toolchain + Node.js/npm pour compiler.
4. Lancer `Compiler-ROMs.cmd`, choisir la console et ajouter les ROMs.
5. Choisir la sortie, laisser la compilation cochee, puis lancer la preparation.
6. Recuperer le `.nwa` et le conteneur associe dans le nouveau dossier resultat.

**Disponibilite :** les sources modifiees compatibles ne sont pas distribuees
dans ce depot actuellement. Les versions amont seules ne garantissent pas le
format multi-ROMs ni les options de scripts attendues. Le depot public de
l'interface ne constitue donc pas un ensemble autonome pret a compiler.
Voir [la verification des licences](LICENSE-REVIEW.md).

Decocher la compilation ne produit que le conteneur ; cela ne dispense pas
de disposer ensuite d'un `.nwa` modifie compatible sur la calculatrice.

## Sur la calculatrice

1. Ouvrir https://my.numworks.com/apps dans un navigateur compatible WebUSB.
2. Selectionner **toutes les applications externes a conserver** : une nouvelle
   installation remplace les autres applications externes.
3. Associer `roms.nes` a `nofrendo.nwa`, ou `roms.gb` a `peanutgb.nwa`.
4. Installer, puis lancer l'emulateur et choisir le jeu dans le menu.

L'outil PC ne lance aucune installation USB automatique. Aucun jeu commercial,
aucune cle API et aucun binaire d'emulateur ne sont fournis par ce depot.
Les modifications ont ete realisees avec assistance IA ; elles ne garantissent
ni la compatibilite de tous les jeux ni les performances du mode Color.