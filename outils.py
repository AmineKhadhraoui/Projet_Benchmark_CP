"""Outils communs : lecture/écriture DIMACS, génération, vérification, heuristiques de base."""
import random


def lire_dimacs(chemin):
    """Lit un fichier .col (format DIMACS). Retourne la liste d'adjacence (liste de listes)."""
    n = 0
    aretes = set()
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            p = ligne.split()
            if not p or p[0] == "c":
                continue
            if p[0] == "p":
                n = int(p[2])
            elif p[0] == "e":
                u, v = int(p[1]) - 1, int(p[2]) - 1
                if u != v:
                    aretes.add((min(u, v), max(u, v)))
    adj = [[] for _ in range(n)]
    for u, v in aretes:
        adj[u].append(v)
        adj[v].append(u)
    return adj


def ecrire_dimacs(chemin, adj, commentaire=""):
    aretes = [(u, v) for u in range(len(adj)) for v in adj[u] if u < v]
    with open(chemin, "w", encoding="utf-8") as f:
        if commentaire:
            f.write(f"c {commentaire}\n")
        f.write(f"p edge {len(adj)} {len(aretes)}\n")
        for u, v in aretes:
            f.write(f"e {u + 1} {v + 1}\n")


def generer_graphe(n, p, graine):
    """Graphe aléatoire G(n, p) : chaque arête existe avec la probabilité p."""
    rng = random.Random(graine)
    adj = [[] for _ in range(n)]
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                adj[u].append(v)
                adj[v].append(u)
    return adj


def nb_aretes(adj):
    return sum(len(a) for a in adj) // 2


def nb_conflits(adj, coloration):
    """Nombre d'arêtes dont les deux extrémités ont la même couleur."""
    return sum(1 for u in range(len(adj)) for v in adj[u] if u < v and coloration[u] == coloration[v])


def nb_couleurs(coloration):
    return len(set(coloration))


def est_valide(adj, coloration):
    return len(coloration) == len(adj) and nb_conflits(adj, coloration) == 0


def dsatur(adj):
    """Heuristique gloutonne DSATUR (Brélaz). Retourne une coloration valide."""
    n = len(adj)
    couleur = [-1] * n
    voisines = [set() for _ in range(n)]
    deg = [len(a) for a in adj]
    for _ in range(n):
        v = max((u for u in range(n) if couleur[u] < 0), key=lambda u: (len(voisines[u]), deg[u]))
        c = 0
        while c in voisines[v]:
            c += 1
        couleur[v] = c
        for u in adj[v]:
            voisines[u].add(c)
    return couleur


def clique_gloutonne(adj):
    """Taille d'une clique trouvée gloutonnement = borne inférieure de χ(G)."""
    n = len(adj)
    ens = [set(a) for a in adj]
    meilleure = 1
    for debut in sorted(range(n), key=lambda u: -len(adj[u]))[:min(n, 50)]:
        clique, cand = [debut], set(ens[debut])
        while cand:
            u = max(cand, key=lambda x: len(ens[x] & cand))
            clique.append(u)
            cand &= ens[u]
        meilleure = max(meilleure, len(clique))
    return meilleure
