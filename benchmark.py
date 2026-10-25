"""Benchmark : compare les algorithmes sur les mêmes instances avec les mêmes critères.

Exemples :
    python benchmark.py                          # tous les algorithmes disponibles
    python benchmark.py --algos exact tabou      # seulement certains
    python benchmark.py --runs 10 --temps 30     # 10 exécutions par instance, 30 s max
Résultat : resultats_<algos>.csv + tableau affiché + graphiques .png
"""
import argparse
import csv
import glob
import importlib
import os
import statistics
import time

from outils import lire_dimacs, nb_aretes, est_valide, nb_couleurs, nb_conflits

# Nom court -> module Python. Ajoutez le vôtre ici si besoin (le fichier doit exister).
MODULES = {
    "exact": "exact",
    "tabou": "tabou",
    "recuit": "recuit",
    "genetique": "genetique",
    "fourmis": "fourmis",
}
DETERMINISTES = {"exact"}      # exécutés une seule fois


def charger(noms):
    algos = {}
    for court, module in MODULES.items():
        if noms and court not in noms:
            continue
        try:
            m = importlib.import_module(module)
            algos[court] = (m.NOM, m.resoudre)
        except ModuleNotFoundError as e:
            if e.name == module:
                if noms:
                    print(f"[!] module '{module}.py' introuvable")
            else:
                raise
    return algos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--algos", nargs="*", default=None)
    ap.add_argument("--runs", type=int, default=10, help="exécutions des algorithmes stochastiques")
    ap.add_argument("--temps", type=float, default=30.0, help="limite de temps (s) par exécution")
    ap.add_argument("--dossier", default="instances")
    args = ap.parse_args()

    algos = charger(args.algos)
    fichiers = sorted(glob.glob(os.path.join(args.dossier, "*.col")),
                      key=lambda f: lire_dimacs(f).__len__())
    lignes = []
    print(f"Algorithmes : {', '.join(n for n, _ in algos.values())} | runs={args.runs} | limite={args.temps}s\n")
    for f in fichiers:
        nom_inst = os.path.splitext(os.path.basename(f))[0]
        adj = lire_dimacs(f)
        print(f"=== {nom_inst} : {len(adj)} sommets, {nb_aretes(adj)} arêtes ===")
        for court, (nom, fonction) in algos.items():
            nb_runs = 1 if court in DETERMINISTES else args.runs
            couleurs, temps, extra = [], [], {}
            for graine in range(nb_runs):
                t0 = time.perf_counter()
                coloration, info = fonction(adj, time_limit=args.temps, seed=graine)
                dt = time.perf_counter() - t0
                if not est_valide(adj, coloration):
                    print(f"  [ERREUR] {nom} : coloration INVALIDE ({nb_conflits(adj, coloration)} conflits) -> ignorée")
                    continue
                couleurs.append(nb_couleurs(coloration))
                temps.append(dt)
                extra = info
            if not couleurs:
                continue
            optimal = extra.get("optimal", "") if court in DETERMINISTES else ""
            ligne = {"instance": nom_inst, "n": len(adj), "m": nb_aretes(adj), "algorithme": nom,
                     "runs": len(couleurs), "meilleur": min(couleurs),
                     "moyenne": round(statistics.mean(couleurs), 2),
                     "ecart_type": round(statistics.pstdev(couleurs), 2),
                     "pire": max(couleurs), "temps_moyen_s": round(statistics.mean(temps), 3),
                     "optimal_prouve": optimal}
            lignes.append(ligne)
            print(f"  {nom:<22} meilleur={ligne['meilleur']:>3}  moyenne={ligne['moyenne']:>6}  "
                  f"pire={ligne['pire']:>3}  temps={ligne['temps_moyen_s']:>8.3f}s  {'(optimum prouvé)' if optimal is True else ''}")
        print()

    # Écart (%) par rapport à la meilleure valeur connue pour l'instance
    for inst in {l["instance"] for l in lignes}:
        ref = min(l["meilleur"] for l in lignes if l["instance"] == inst)
        for l in lignes:
            if l["instance"] == inst:
                l["ref_meilleure_connue"] = ref
                l["ecart_pct"] = round(100 * (l["moyenne"] - ref) / ref, 1)
    nom_csv = "resultats_" + "_".join(algos) + ".csv"
    with open(nom_csv, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(lignes[0].keys()), delimiter=";")
        w.writeheader()
        w.writerows(lignes)
    print(f"Résultats enregistrés dans {nom_csv}")


if __name__ == "__main__":
    main()
