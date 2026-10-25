# Benchmark – Coloration de graphes (instructions pour les membres de l'équipe)

## 1. Variante et critères COMMUNS (à ne pas changer)
- **Variante** : coloration de sommets classique (minimiser le nombre de couleurs χ(G)), graphes simples non orientés.
- **Données** : les 3 fichiers du dossier `instances/` (format DIMACS .col), identiques pour tous :
  | Échantillon | Fichier | Sommets | Arêtes |
  |---|---|---|---|
  | Petit | petit_n20.col | 20 | 63 |
  | Moyen | moyen_n60.col | 60 | 533 |
  | Grand | grand_n200.col | 200 | 9886 |
- **Paramètres communs** : limite de temps 30 s par exécution, 10 exécutions (graines 0 à 9) pour les algorithmes stochastiques.
- **Critères de comparaison** : (1) nombre de couleurs (meilleur / moyenne / pire), (2) temps d'exécution moyen,
  (3) écart (%) à la meilleure valeur connue, (4) complexité théorique, (5) robustesse (écart-type).
- **Algorithme exact** : fourni (`exact.py`, backtracking avec élagage DSATUR). Ne pas le modifier.

## 2. Ce que chacun doit faire (une métaheuristique par membre)
Choix possibles : recuit simulé, algorithme génétique, colonies de fourmis (la recherche tabou est prise).
1. Installer Python 3 et `pip install numpy matplotlib`.
2. Décompresser le dossier, copier `modele_algorithme.py` en `recuit.py` (ou `genetique.py` / `fourmis.py`).
3. Écrire (ou faire générer par ChatGPT/Blackbox) l'algorithme dans la fonction `resoudre(adj, time_limit, seed)`.
   Exigences : respecter la limite de temps, retourner une coloration VALIDE, être reproductible via `seed`.
4. Lancer : `python benchmark.py --algos recuit` (remplacer par votre nom). Un fichier `resultats_recuit.csv` est créé.
5. Envoyer à la personne qui fusionne : votre fichier .py et votre fichier `resultats_*.csv`.
6. Rédiger votre partie : pseudo-code (Q1), paramètres (Q2), complexité (Q3), résultats et conclusions (Q5).
7. Pour fusionner : mettre tous les `resultats_*.csv` dans un même dossier et lancer `python fusionner_resultats.py`.
