"""Algorithme génétique (hybride) pour la coloration de graphes.

Principe : on fixe k. Un individu = une coloration avec k couleurs (éventuellement invalide) ;
sa qualité (fitness) = nombre d'arêtes en conflit à minimiser. La population évolue par :
  - sélection par tournoi (2 parents),
  - croisement GPX (Greedy Partition Crossover) : l'enfant hérite alternativement de la plus
    grande classe de couleur de chaque parent, les sommets restants sont recolorés au hasard,
  - mutation : recoloration aléatoire d'un petit nombre de sommets en conflit,
  - amélioration locale courte (descente stochastique) sur chaque enfant (algorithme mémétique),
  - remplacement du plus mauvais individu (population à état stationnaire).
Quand un individu a f = 0, on retire une couleur (k-1) et on recommence, jusqu'à échec ou fin du temps.

Paramètres : TAILLE_POP, TAUX_MUTATION, PAS_RECHERCHE_LOCALE, MAX_GENERATIONS (par valeur de k).
Complexité : O(MAX_GENERATIONS * (n*k + m + PAS_RECHERCHE_LOCALE * n)) par valeur de k
(croisement O(n*k), construction de gamma O(m), chaque pas de recherche locale O(n + k + deg)).
"""
import random
import time
from outils import dsatur

NOM = "Algorithme génétique"
TAILLE_POP = 20            # nombre d'individus
TAUX_MUTATION = 0.3        # probabilité de muter un enfant
NB_MUTES = 3               # nombre de sommets recolorés lors d'une mutation
PAS_RECHERCHE_LOCALE = 400 # itérations de la descente stochastique appliquée à chaque enfant
MAX_GENERATIONS = 1500     # nombre d'enfants créés pour chaque valeur de k


def construire_gamma(adj, c, k):
    gamma = [[0] * k for _ in range(len(adj))]
    for v in range(len(adj)):
        g = gamma[v]
        for u in adj[v]:
            g[c[u]] += 1
    return gamma


def conflits(adj, c):
    return sum(1 for v in range(len(adj)) for u in adj[v] if u < v and c[u] == c[v])


def recherche_locale(adj, c, k, pas, rng):
    """Descente stochastique : un sommet en conflit prend sa meilleure couleur (mouvements neutres
    acceptés). Retourne (coloration améliorée, f)."""
    n = len(adj)
    c = c[:]
    gamma = construire_gamma(adj, c, k)
    f = sum(gamma[v][c[v]] for v in range(n)) // 2
    for _ in range(pas):
        if f == 0:
            break
        en_conflit = [v for v in range(n) if gamma[v][c[v]] > 0]
        v = en_conflit[rng.randrange(len(en_conflit))]
        g, ancienne = gamma[v], c[v]
        meilleur = min(g[col] for col in range(k) if col != ancienne)
        col = rng.choice([x for x in range(k) if x != ancienne and g[x] == meilleur])
        delta = g[col] - g[ancienne]
        if delta > 0:
            continue
        c[v] = col
        f += delta
        for u in adj[v]:
            gamma[u][ancienne] -= 1
            gamma[u][col] += 1
    return c, f


def croisement_gpx(p1, p2, k, rng):
    """GPX : l'enfant reçoit alternativement la plus grande classe de p1 puis de p2."""
    n = len(p1)
    classes = []
    for p in (p1, p2):
        cl = [set() for _ in range(k)]
        for v in range(n):
            cl[p[v]].add(v)
        classes.append(cl)
    enfant = [-1] * n
    for i in range(k):
        cl = classes[i % 2]
        j = max(range(k), key=lambda x: len(cl[x]))
        choisis = set(cl[j])
        for v in choisis:
            enfant[v] = i
        for cc in classes:
            for ens in cc:
                ens -= choisis
    for v in range(n):                      # sommets restants : couleur aléatoire
        if enfant[v] < 0:
            enfant[v] = rng.randrange(k)
    return enfant


def evoluer_k(adj, depart, k, max_gen, rng, limite_temps):
    """Cherche une k-coloration valide. Retourne (coloration, f_finale)."""
    n = len(adj)
    pop = []
    for i in range(TAILLE_POP):
        if i == 0:
            ind = depart[:]
        else:
            ind = [rng.randrange(k) for _ in range(n)]
        ind, f = recherche_locale(adj, ind, k, PAS_RECHERCHE_LOCALE, rng)
        if f == 0:
            return ind, 0
        pop.append((f, ind))
    for gen in range(max_gen):
        if time.perf_counter() > limite_temps:
            break
        # sélection par tournoi binaire
        a = min(rng.sample(pop, 2), key=lambda x: x[0])
        b = min(rng.sample(pop, 2), key=lambda x: x[0])
        enfant = croisement_gpx(a[1], b[1], k, rng)
        if rng.random() < TAUX_MUTATION:
            for _ in range(NB_MUTES):
                enfant[rng.randrange(n)] = rng.randrange(k)
        enfant, f = recherche_locale(adj, enfant, k, PAS_RECHERCHE_LOCALE, rng)
        if f == 0:
            return enfant, 0
        # remplacement du plus mauvais individu
        pire = max(range(len(pop)), key=lambda i: pop[i][0])
        if f <= pop[pire][0]:
            pop[pire] = (f, enfant)
    meilleur = min(pop, key=lambda x: x[0])
    return meilleur[1], meilleur[0]


def resoudre(adj, time_limit=30.0, seed=0):
    debut = time.perf_counter()
    limite = debut + time_limit
    rng = random.Random(seed)
    meilleure = dsatur(adj)                        # solution initiale gloutonne
    k = max(meilleure) + 1
    k_testes = 0
    while k > 2 and time.perf_counter() < limite:
        k -= 1
        depart = [c if c < k else rng.randrange(k) for c in meilleure]
        sol, f = evoluer_k(adj, depart, k, MAX_GENERATIONS, rng, limite)
        k_testes += 1
        if f == 0:
            meilleure = sol
        else:
            break
    return meilleure, {"valeurs_k_testees": k_testes}
