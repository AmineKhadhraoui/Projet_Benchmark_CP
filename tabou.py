"""Recherche tabou (TabuCol) pour la coloration de graphes.

Principe : on fixe k, on part d'une coloration avec k couleurs (éventuellement invalide) et on
minimise f(c) = nombre d'arêtes en conflit en recolorant un sommet en conflit à chaque itération.
Quand f = 0, on retire une couleur (k-1) et on recommence, jusqu'à échec ou fin du temps.

Paramètres : L (aléa de la durée tabou), ALPHA (poids des conflits), MAX_ITER (itérations par k).
Durée tabou : t = L_aleatoire[0..9] + ALPHA * f(c)
"""
import time
import numpy as np
from outils import dsatur

NOM = "Recherche tabou"
L_MAX = 10        # durée tabou : entier aléatoire dans [0, L_MAX - 1]
ALPHA = 0.6       # durée tabou : + ALPHA * (nombre de conflits)
MAX_ITER = 50000  # nombre maximal d'itérations pour chaque valeur de k


def tabucol(adj_np, coloration, k, max_iter, rng, limite_temps):
    """Cherche une k-coloration valide. Retourne (coloration, f_finale)."""
    n = len(adj_np)
    c = np.array(coloration, dtype=np.int64)
    gamma = np.zeros((n, k), dtype=np.int64)      # gamma[v][col] = nb de voisins de v de couleur col
    for v in range(n):
        np.add.at(gamma[v], c[adj_np[v]], 1)
    lignes = np.arange(n)
    f = int(gamma[lignes, c].sum() // 2)
    tabou = np.zeros((n, k), dtype=np.int64)       # itération jusqu'à laquelle (v, col) est interdit
    meilleur_f, meilleure_c = f, c.copy()
    it = 0
    while f > 0 and it < max_iter:
        if (it & 255) == 0 and time.perf_counter() > limite_temps:
            break
        actuel = gamma[lignes, c]
        en_conflit = actuel > 0
        delta = gamma - actuel[:, None]            # variation de f si v prend la couleur col
        delta[lignes, c] = 10 ** 9                 # on ne garde pas la même couleur
        delta[~en_conflit, :] = 10 ** 9            # seuls les sommets en conflit bougent
        admis = (tabou <= it) | (f + delta < meilleur_f)   # non tabou OU aspiration
        delta_ok = np.where(admis, delta, 10 ** 9)
        m = delta_ok.min()
        if m >= 10 ** 9:                           # tout est tabou : mouvement aléatoire
            cand = np.argwhere(en_conflit[:, None] & (delta < 10 ** 9))
        else:
            cand = np.argwhere(delta_ok == m)
        if len(cand) == 0:
            break
        v, col = cand[rng.integers(len(cand))]
        ancienne = c[v]
        t = int(rng.integers(L_MAX) + ALPHA * f)
        tabou[v, ancienne] = it + t + 1            # interdit de redonner l'ancienne couleur
        f += int(gamma[v, col] - gamma[v, ancienne])
        voisins = adj_np[v]
        gamma[voisins, ancienne] -= 1
        gamma[voisins, col] += 1
        c[v] = col
        if f < meilleur_f:
            meilleur_f, meilleure_c = f, c.copy()
        it += 1
    return meilleure_c.tolist(), meilleur_f


def resoudre(adj, time_limit=30.0, seed=0):
    debut = time.perf_counter()
    limite = debut + time_limit
    rng = np.random.default_rng(seed)
    adj_np = [np.array(a, dtype=np.int64) for a in adj]
    n = len(adj)
    meilleure = dsatur(adj)                        # solution initiale gloutonne
    k = max(meilleure) + 1
    iterations_k = 0
    while k > 1 and time.perf_counter() < limite:
        if k <= 2:
            break
        k -= 1
        # on retire la couleur k : ses sommets reçoivent une couleur aléatoire
        depart = [c if c < k else int(rng.integers(k)) for c in meilleure]
        sol, f = tabucol(adj_np, depart, k, MAX_ITER, rng, limite)
        iterations_k += 1
        if f == 0:
            meilleure = sol
        else:
            break
    return meilleure, {"valeurs_k_testees": iterations_k}
