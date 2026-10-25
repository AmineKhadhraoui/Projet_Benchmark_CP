"""Fusionne tous les resultats_*.csv du dossier, affiche le tableau final et crée les graphiques.
Usage : python fusionner_resultats.py"""
import csv
import glob
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

lignes = []
for f in sorted(glob.glob("resultats_*.csv")):
    if f == "resultats_final.csv":
        continue
    with open(f, encoding="utf-8-sig") as fh:
        lignes += list(csv.DictReader(fh, delimiter=";"))

# on garde une seule ligne par (instance, algorithme) ; l'écart est recalculé sur l'ensemble
vu, uniq = set(), []
for l in lignes:
    cle = (l["instance"], l["algorithme"])
    if cle not in vu:
        vu.add(cle)
        uniq.append(l)
lignes = uniq
for inst in {l["instance"] for l in lignes}:
    ref = min(int(l["meilleur"]) for l in lignes if l["instance"] == inst)
    for l in lignes:
        if l["instance"] == inst:
            l["ref_meilleure_connue"] = ref
            l["ecart_pct"] = round(100 * (float(l["moyenne"]) - ref) / ref, 1)
lignes.sort(key=lambda l: (int(l["n"]), l["algorithme"]))

with open("resultats_final.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(lignes[0].keys()), delimiter=";")
    w.writeheader()
    w.writerows(lignes)

print(f"{'Instance':<12}{'Algorithme':<22}{'Meilleur':>9}{'Moyenne':>9}{'Pire':>6}{'Temps(s)':>10}{'Écart%':>8}")
for l in lignes:
    print(f"{l['instance']:<12}{l['algorithme']:<22}{l['meilleur']:>9}{l['moyenne']:>9}{l['pire']:>6}{l['temps_moyen_s']:>10}{l['ecart_pct']:>8}")

instances = sorted({l["instance"] for l in lignes}, key=lambda i: int(next(l["n"] for l in lignes if l["instance"] == i)))
algos = sorted({l["algorithme"] for l in lignes})
for cle, titre, fichier, log in [("moyenne", "Nombre moyen de couleurs (plus petit = meilleur)", "graphique_couleurs.png", False),
                                 ("temps_moyen_s", "Temps d'exécution moyen en secondes (échelle log)", "graphique_temps.png", True)]:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    largeur = 0.8 / len(algos)
    for j, a in enumerate(algos):
        vals = [float(next((l[cle] for l in lignes if l["instance"] == i and l["algorithme"] == a), 0)) for i in instances]
        ax.bar([x + j * largeur for x in range(len(instances))], vals, largeur, label=a)
    ax.set_xticks([x + 0.4 - largeur / 2 for x in range(len(instances))])
    ax.set_xticklabels(instances)
    ax.set_title(titre)
    if log:
        ax.set_yscale("log")
    ax.legend()
    fig.tight_layout()
    fig.savefig(fichier, dpi=150)
print("\nGraphiques : graphique_couleurs.png, graphique_temps.png | tableau : resultats_final.csv")
