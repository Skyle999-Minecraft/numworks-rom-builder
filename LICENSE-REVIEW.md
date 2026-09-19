# Verification des licences des dependances

Cette note rapporte les documents consultes ; elle ne constitue pas un avis
juridique ni une autorisation accordee par les auteurs des logiciels tiers.
Les liens vers une branche peuvent evoluer apres cette verification.

## PeanutGB pour NumWorks

- Portage : https://github.com/nwagyu/peanutgb
- La racine du depot et son README ne fournissent pas de licence globale.
- Le fichier d'integration `src/main.c` amont ne contient pas de licence explicite.
- Le coeur `peanut_gb.h` porte une notice **MIT**, avec attribution a Mahyar
  Koshkouei et aux portions de SameBoy de Lior Halphon.
- La licence du coeur ne prouve pas a elle seule celle du code d'integration,
  des modifications apportees par d'autres auteurs ou de l'icone du portage.
- Aucune clarification de licence n'a ete trouvee dans les issues consultees.

Pour le coeur Color utilise localement :

- https://github.com/PicoPlus-devel/pico-peanutGB
- https://github.com/PicoPlus-devel/pico-peanutGB/blob/master/LICENSE
- Le depot porte une licence globale **GPLv3** ; la copie locale de son fichier
  `peanut_gb.h` contient une notice **MIT**. Ce constat ne justifie pas de
  presenter tous les fichiers et toutes les modifications du projet comme MIT.
  La provenance et la portee des notices doivent etre conservees et clarifiees.

## Nofrendo pour NumWorks

- Portage : https://codeberg.org/Yaya-Cout/nofrendo
- Origine : https://github.com/nwagyu/nofrendo
- Pas de licence globale explicite a la racine ni dans les README consultes.
- Le coeur Nofrendo porte des notices **GNU Library General Public License,
  version 2**, notamment au nom de Matthew Conte.
- LZ4 porte sa notice **BSD 2-Clause**, au nom de Yann Collet.
- Certains fichiers se declarent dans le domaine public.
- Plusieurs fichiers d'integration ne donnent pas de licence explicite.
- `libsnss.c` et `libsnss.h` renvoient a un `README.TXT` pour leurs conditions ;
  ce document manque dans la copie et les arbres des portages consultes.

## Ce qui ne permet pas de conclure

Le projet d'exemple C de NumWorks possede une licence BSD-3-Clause :
https://github.com/numworks/epsilon-sample-app-c/blob/master/LICENSE
Cette licence ne peut pas etre automatiquement attribuee a d'autres portages
ou aux ajouts de leurs auteurs sans verifier leur provenance et leurs droits.

Un depot public sans licence n'accorde pas automatiquement les droits generaux
de redistribuer une version modifiee. GitHub distingue ces droits des fonctions
de consultation et de fork offertes par sa plateforme :
https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository

## Conclusion et etapes necessaires

La redistribution des **portages complets modifies** n'est pas suffisamment
etablie par les documents trouves. Ils ne sont donc pas distribues ici, ni en
sources, ni en binaires. Cette conclusion signifie « autorisation non etablie »,
pas « interdiction explicite trouvee ».

Avant publication, obtenir une clarification des mainteneurs sur le code
d'integration, l'icone, les ajouts Color et les conditions de libsnss ; conserver
les textes applicables, les credits, la provenance et la liste des modifications.
Ajouter des credits ou une mention IA ne remplace pas ces autorisations.

## Demandes de clarification envoyees

Avec l'autorisation du proprietaire du compte, trois demandes publiques ont ete
envoyees. Elles mentionnent explicitement leur redaction avec assistance IA :

- Portage PeanutGB : https://github.com/nwagyu/peanutgb/issues/3
- Portage Nofrendo et conditions libsnss : https://github.com/nwagyu/nofrendo/issues/5
- Portee des licences du coeur Color : https://github.com/PicoPlus-devel/pico-peanutGB/issues/12

Leur envoi ne vaut pas autorisation de redistribution : les reponses restent
a examiner avant publication des portages. La demande concernant les ajouts
de Yaya-Cout sur Codeberg est seulement un brouillon local, non envoye.