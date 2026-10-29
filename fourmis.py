"""Colonies de fourmis (de type ANTCOL / MAX-MIN Ant System) pour la coloration de graphes.

Principe : contrairement à tabou/recuit/génétique, on ne fixe pas k. Chaque fourmi CONSTRUIT une
coloration valide classe de couleur par classe de couleur (à la manière de RLF) :
  - on ouvre une nouvelle couleur avec le sommet non colorié de plus grand degré restant,
  - on ajoute ensuite des sommets non adjacents à la classe, choisis avec la probabilité
        p(v) proportionnelle à  tau(v, classe)^ALPHA * eta(v)^BETA
    tau(v, classe) = phéromone moyenne entre v et les sommets déjà dans la classe,
    eta(v)         = degré de v parmi les sommets encore non coloriés (heuristique),
  - on recommence jusqu'à ce que tous les sommets soient coloriés.
Phéromone tau(u, v) : désir de mettre u et v dans la MÊME couleur. Après chaque itération :
évaporation (RHO), puis dépôt sur les paires de même classe par la meilleure fourmi de l'itération
et par la meilleure solution globale, avec des bornes [TAU_MIN, TAU_MAX] (MAX-MIN).

Paramètres : NB_FOURMIS, ALPHA, BETA, RHO, STAGNATION (itérations sans amélioration avant arrêt).
Complexité : O(NB_ITER * NB_FOURMIS * n^2) (chaque fourmi fait n choix, chacun en O(n)).
"""
import time
import numpy as np
from outils import dsatur

NOM = "Colonies de fourmis"
NB_FOURMIS = 10
ALPHA = 2.0        # poids de la phéromone
BETA = 2.0         # poids de l'heuristique (degré restant)
RHO = 0.1          # taux d'évaporation
TAU_MIN, TAU_MAX = 0.1, 5.0
STAGNATION = 200   # arrêt après ce nombre d'itérations sans amélioration


def fourmi_construit(A, tau, rng):
    """Une fourmi construit une coloration valide. A = matrice d'adjacence booléenne."""
    n = len(A)
    couleur = np.full(n, -1, dtype=np.int64)
    non_colorie = np.ones(n, dtype=bool)
    deg_restant = A.sum(axis=1).astype(np.float64)
    nb = 0
    while non_colorie.any():
        # nouvelle classe : sommet de plus grand degré restant (aléa entre ex aequo)
        score = np.where(non_colorie, deg_restant + rng.random(n) * 0.5, -1.0)
        v = int(score.argmax())
        classe = [v]
        candidats = non_colorie & ~A[v]
        candidats[v] = False
        somme_tau = tau[v].copy()
        while candidats.any():
            idx = np.flatnonzero(candidats)
            poids = (somme_tau[idx] / len(classe)) ** ALPHA * (deg_restant[idx] + 1.0) ** BETA
            cumul = np.cumsum(poids)
            v = int(idx[np.searchsorted(cumul, rng.random() * cumul[-1])])
            classe.append(v)
            somme_tau += tau[v]
            candidats &= ~A[v]
            candidats[v] = False
        couleur[classe] = nb
        non_colorie[classe] = False
        deg_restant -= A[classe].sum(axis=0)
        nb += 1
    return couleur, nb


def deposer(tau, couleur, nb, quantite):
    for c in range(nb):
        membres = np.flatnonzero(couleur == c)
        if len(membres) > 1:
            tau[np.ix_(membres, membres)] += quantite


def resoudre(adj, time_limit=30.0, seed=0):
    debut = time.perf_counter()
    limite = debut + time_limit
    rng = np.random.default_rng(seed)
    n = len(adj)
    A = np.zeros((n, n), dtype=bool)
    for v in range(n):
        A[v, adj[v]] = True
    tau = np.full((n, n), TAU_MAX)

    meilleure = dsatur(adj)                         # solution initiale valide
    meilleur_nb = max(meilleure) + 1
    meilleure_np = np.array(meilleure)
    sans_amelioration, iteration = 0, 0
    while time.perf_counter() < limite and sans_amelioration < STAGNATION:
        iteration += 1
        meilleure_iter, nb_iter = None, n + 1
        for _ in range(NB_FOURMIS):
            if time.perf_counter() > limite:
                break
            col, nb = fourmi_construit(A, tau, rng)
            if nb < nb_iter:
                meilleure_iter, nb_iter = col, nb
        if meilleure_iter is None:
            break
        if nb_iter < meilleur_nb:
            meilleur_nb, meilleure_np = nb_iter, meilleure_iter.copy()
            sans_amelioration = 0
        else:
            sans_amelioration += 1
        tau *= (1.0 - RHO)                          # évaporation
        deposer(tau, meilleure_iter, nb_iter, 1.0 / nb_iter * 2)
        deposer(tau, meilleure_np, meilleur_nb, 1.0 / meilleur_nb * 2)
        np.clip(tau, TAU_MIN, TAU_MAX, out=tau)
    return [int(c) for c in meilleure_np], {"iterations": iteration}
