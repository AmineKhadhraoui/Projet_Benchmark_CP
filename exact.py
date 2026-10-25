"""Algorithme EXACT : backtracking avec élagage (Branch & Bound de type DSATUR).

- On colorie le sommet de plus grande saturation en premier.
- On n'essaie que les couleurs déjà utilisées + UNE nouvelle (symétries évitées).
- On élague dès que le nombre de couleurs atteint la meilleure solution connue.
- Une limite de temps est imposée : si elle est atteinte, on renvoie la meilleure solution
  trouvée (optimal = False).
"""
import sys
import time
from outils import dsatur, clique_gloutonne

NOM = "Exact (B&B DSATUR)"


class _Fin(Exception):
    pass


def resoudre(adj, time_limit=60.0, seed=0):
    sys.setrecursionlimit(10000)
    n = len(adj)
    debut = time.perf_counter()
    meilleure = dsatur(adj)
    ub = max(meilleure) + 1                 # meilleure borne supérieure
    lb = clique_gloutonne(adj)              # borne inférieure
    info = {"optimal": ub == lb, "noeuds": 0}
    if ub == lb:
        return meilleure, info

    deg = [len(a) for a in adj]
    couleur = [-1] * n
    cnt = [[0] * (n + 1) for _ in range(n)]   # cnt[v][c] = nb de voisins de v de couleur c
    sat = [0] * n

    def rec(nb_colores, utilisees):
        nonlocal ub, meilleure
        info["noeuds"] += 1
        if info["noeuds"] % 500 == 0 and time.perf_counter() - debut > time_limit:
            info["optimal"] = False
            raise _Fin
        if nb_colores == n:
            ub = utilisees
            meilleure = couleur[:]
            if ub == lb:
                raise _Fin
            return
        v = max((u for u in range(n) if couleur[u] < 0), key=lambda u: (sat[u], deg[u]))
        for c in range(min(utilisees, ub - 2) + 1):
            if cnt[v][c] == 0:
                couleur[v] = c
                for u in adj[v]:
                    if cnt[u][c] == 0:
                        sat[u] += 1
                    cnt[u][c] += 1
                rec(nb_colores + 1, max(utilisees, c + 1))
                for u in adj[v]:
                    cnt[u][c] -= 1
                    if cnt[u][c] == 0:
                        sat[u] -= 1
                couleur[v] = -1

    info["optimal"] = True
    try:
        rec(0, 0)
    except _Fin:
        pass
    if ub == lb:
        info["optimal"] = True
    info["borne_inf"] = lb
    return meilleure, info
