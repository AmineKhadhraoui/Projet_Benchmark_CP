"""Recuit simulé pour la coloration de graphes.

Principe : on fixe k, on part d'une coloration avec k couleurs (éventuellement invalide) et on
minimise f(c) = nombre d'arêtes en conflit. À chaque itération on choisit un sommet en conflit et
une nouvelle couleur au hasard ; le mouvement est accepté si delta <= 0, sinon avec la probabilité
exp(-delta / T) (critère de Metropolis). La température T décroît géométriquement.
Quand f = 0, on retire une couleur (k-1) et on recommence, jusqu'à échec ou fin du temps.

Paramètres : T0 (température initiale), T_MIN (température finale), MAX_ITER (itérations par k).
Refroidissement : T(it) = T0 * (T_MIN / T0) ** (it / MAX_ITER)
Complexité : O(MAX_ITER * deg_moyen) par valeur de k (mise à jour de la table gamma des voisins).
"""
import math
import random
import time
from outils import dsatur

NOM = "Recuit simulé"
T0 = 0.5           # température initiale
T_MIN = 0.15       # température finale
MAX_ITER = 1000000  # nombre d'itérations (une descente de température) pour chaque valeur de k
REDEMARRAGES = 2   # nombre de cycles de refroidissement tentés pour chaque k avant d'abandonner


def recuit_k(adj, coloration, k, max_iter, rng, limite_temps):
    """Cherche une k-coloration valide par recuit simulé. Retourne (coloration, f_finale)."""
    n = len(adj)
    c = list(coloration)
    gamma = [[0] * k for _ in range(n)]            # gamma[v][col] = nb de voisins de v de couleur col
    for v in range(n):
        g = gamma[v]
        for u in adj[v]:
            g[c[u]] += 1
    f = sum(gamma[v][c[v]] for v in range(n)) // 2

    # liste des sommets en conflit, avec position pour ajout/retrait en O(1)
    conf, pos = [], [-1] * n

    def ajouter(v):
        if pos[v] < 0:
            pos[v] = len(conf)
            conf.append(v)

    def retirer(v):
        p = pos[v]
        if p >= 0:
            dernier = conf.pop()
            if dernier != v:
                conf[p] = dernier
                pos[dernier] = p
            pos[v] = -1

    for v in range(n):
        if gamma[v][c[v]] > 0:
            ajouter(v)

    meilleur_f, meilleure_c = f, c[:]
    facteur = (T_MIN / T0) ** (1.0 / max_iter)
    T = T0
    for it in range(max_iter):
        if f == 0:
            break
        if (it & 1023) == 0 and time.perf_counter() > limite_temps:
            break
        v = conf[rng.randrange(len(conf))]
        ancienne = c[v]
        col = rng.randrange(k - 1)
        if col >= ancienne:
            col += 1                                # couleur différente de l'ancienne
        g = gamma[v]
        delta = g[col] - g[ancienne]
        if delta <= 0 or rng.random() < math.exp(-delta / T):
            c[v] = col
            f += delta
            for u in adj[v]:
                gu = gamma[u]
                gu[ancienne] -= 1
                gu[col] += 1
                cu = c[u]
                if cu == ancienne:
                    if gu[cu] == 0:
                        retirer(u)
                elif cu == col:
                    ajouter(u)
            if g[col] > 0:
                ajouter(v)
            else:
                retirer(v)
            if f < meilleur_f:
                meilleur_f, meilleure_c = f, c[:]
        T *= facteur
    return meilleure_c, meilleur_f


def resoudre(adj, time_limit=30.0, seed=0):
    debut = time.perf_counter()
    limite = debut + time_limit
    rng = random.Random(seed)
    n = len(adj)
    meilleure = dsatur(adj)                        # solution initiale gloutonne
    k = max(meilleure) + 1
    k_testes = 0
    while k > 2 and time.perf_counter() < limite:
        k -= 1
        # on retire la couleur k : ses sommets reçoivent une couleur aléatoire
        depart = [c if c < k else rng.randrange(k) for c in meilleure]
        trouve = False
        for _ in range(REDEMARRAGES):
            sol, f = recuit_k(adj, depart, k, MAX_ITER, rng, limite)
            if f == 0:
                trouve = True
                break
            if time.perf_counter() >= limite:
                break
        k_testes += 1
        if trouve:
            meilleure = sol
        else:
            break
    return meilleure, {"valeurs_k_testees": k_testes}
