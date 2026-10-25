# Mode d'emploi rapide
1. Installer Python 3.10+ (python.org) en cochant « Add Python to PATH ».
2. Ouvrir un terminal dans ce dossier et taper : `pip install numpy matplotlib`
3. Lancer le benchmark : `python benchmark.py --algos exact tabou --runs 10 --temps 30`
4. Générer tableau + graphiques : `python fusionner_resultats.py`
Fichiers : outils.py (lecture/vérification), exact.py (algo exact), tabou.py (recherche tabou),
benchmark.py (comparaison), fusionner_resultats.py (tableau + graphiques), instances/ (données).
Les fichiers `resultats_exact_tabou.csv`, `resultats_final.csv`, `graphique_*.png` sont mes résultats d'exemple.
