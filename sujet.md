# Projet-CSP
## M2 IA Université d'Angers
### Résolution de Problème Avancée 2023/2024
### Projet n°1 : Set Constraint Modelling and Solving

**The Social Golfer Problem (SGP)**
Le Social Golfer Problem (problème numéro 10 de la CSPLib) est le suivant : q golfeurs jouent chaque semaine pendant w semaines, répartis en g groupes de p golfeurs (q = p.g). Comment planifier le jeu de ces golfeurs de telle sorte qu'aucun golfeur ne joue dans le même groupe qu'un autre golfeur plus d'une fois ?

Diverses instances du Social Golfer Problem sont encore ouvertes, et le problème est attractif car il est lié à des problèmes tels que le chiffrement et les problèmes de couverture.
(Problème numéro 26 de la CSPLib)

### 1. Modélisation

#### 1.1 Modèles initiaux
Modélisez le SGP par un modèle de contraintes ensemblistes. Plusieurs modélisations sont possibles, n'hésitez pas à donner des variantes. Commentez les différences et similitudes entre modèles.

#### 1.2 Modèles améliorés
Améliorez les modèles ci-dessus :
1. Trouvez des symétries et essayez de les casser dans les modèles où c'est possible ;
2. Pensez aux contraintes redondantes qui seraient possibles.

Commentez et argumentez les améliorations selon les modèles. Comparez et analysez bien les symétries selon les modèles.

#### 1.3 Résolution
1. Implantez les modèles ci-dessus (au choix : MiniZinc, ECLiPSe, Essence, ...);
2. Comparez ces différents modèles pour diverses instances du SGP ;
3. Analysez les résultats obtenus (comparaisons entre les modèles, le cassage de symétries, ce qui est faisable dans un modèle et pas dans un autre, etc.). Le SGP est basé sur 3 paramètres, peut-être est-il judicieux d'en fixer certains, ou en tout cas, de ne pas les faire varier de façon aléatoire. Donnez une orientation à votre étude comme un thème de recherche (influence d'un paramètre sur les autres, les symétries, la transition de phase, ...);
4. Proposez des améliorations, même si vous n'êtes pas en mesure de pouvoir les faire.

### 2. Solveur pour les contraintes ensemblistes

Il faudra bien sûr régler des problèmes de langage admissible, puissance recherchée, langage d'implantation, etc. Les solveurs réalisés seront testés sur les instances ensemblistes vues au-dessus. Il y aura bien sûr une phase d'analyse très développée. Au niveau des langages pour la modélisation et des fonctionnalités, n'essayez pas d'être extensifs au début, mais de couvrir les besoins liés à vos modèles du SGP. Vous pourrez ensuite améliorer pour rendre le solveur plus générique.

Solveur ensembliste : modélisation avec des contraintes ensemblistes, et résolution de celles-ci. Implantez un solveur ensembliste à base de propagation de contraintes (filtrage de contraintes ensemblistes). Vous avez le choix de la consistance locale, ou vous pouvez aussi tenter d'en comparer deux. L'énumération est également libre.

Comparez et analysez les résultats obtenus, également avec la partie précédente.

### 3. Délivrables

Trois parties seront considérées : le travail effectué, un rapport, et une présentation orale. Une attention particulière devra surtout être apportée aux analyses, à la recherche de solutions éventuelles permettant d'améliorer les réalisations, etc. Vous aurez à lire quelques articles afin d'être plus à l'aise.

Voici des points de départ possibles :

- **Conjunto** : Carmen Gervet, Conjunto : Constraint Logic Programming with Finite Set Domains, ILPS 1994, pp. 339-358.
- **Cardinal** : Francisco Azevedo, Cardinal : A Finite Sets Constraint Solver. Constraints 12(1) : 93-129 (2007)
- **Cardinality** : Bailleux, O., Boufkhad, Y. Efficient CNF Encoding of Boolean Cardinality Constraints. In CP 2003, pp. 108-122.
- **minSet** : Correas, J., Martín, S. E., Saenz-Perez, F. Enhancing set constraint solvers with bound consistency. Expert Systems with Applications, 2018, 92:485-494.
