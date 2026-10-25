"""Génère les 3 échantillons du benchmark (graphes aléatoires G(n, p), graines fixes).
NE PAS relancer si vous utilisez déjà les fichiers fournis : tout le groupe doit garder les mêmes."""
import os
from outils import generer_graphe, ecrire_dimacs, nb_aretes

INSTANCES = [            # (nom, n sommets, p densité, graine)
    ("petit_n20",   20, 0.30, 11),
    ("moyen_n60",   60, 0.30, 22),
    ("grand_n200", 200, 0.50, 33),
]

if __name__ == "__main__":
    os.makedirs("instances", exist_ok=True)
    for nom, n, p, graine in INSTANCES:
        adj = generer_graphe(n, p, graine)
        ecrire_dimacs(f"instances/{nom}.col", adj, f"G({n},{p}) graine={graine}")
        print(f"{nom}: {n} sommets, {nb_aretes(adj)} arêtes")
