"""MODÈLE à copier pour votre métaheuristique (recuit simulé, génétique, fourmis, ...).

1. Copiez ce fichier : recuit.py, genetique.py ou fourmis.py (voir noms dans benchmark.py).
2. Gardez la même fonction  resoudre(adj, time_limit, seed)  :
   - adj  : liste d'adjacence (adj[v] = liste des voisins du sommet v, sommets numérotés de 0 à n-1)
   - time_limit : temps maximal en secondes (ne jamais le dépasser)
   - seed : graine aléatoire (pour que les résultats soient reproductibles)
   - retour : (coloration, info)  où coloration[v] = couleur du sommet v (entier >= 0),
     et info = dictionnaire (peut être vide {}).
3. La coloration retournée DOIT être valide (aucun conflit) : le benchmark le vérifie.
"""
import random
import time
from outils import dsatur

NOM = "Mon algorithme"          # <-- nom affiché dans les tableaux


def resoudre(adj, time_limit=30.0, seed=0):
    debut = time.perf_counter()
    rng = random.Random(seed)
    meilleure = dsatur(adj)      # <-- remplacez par votre algorithme (partez d'une solution valide)
    while time.perf_counter() - debut < time_limit:
        break                    # <-- votre boucle de recherche ici
    return meilleure, {}
