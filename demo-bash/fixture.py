"""
Construit un arbre de test reproductible pour archive.sh.

Les dates de modification sont posees explicitement : sans ca, aucun test
de comportement n'est possible. C'est le meme principe que la date de
reference injectable, et c'est deja la moitie de l'exercice.

    python3 fixture.py bac/
"""

import os
import shutil
import sys

# Ancre temporelle fixe : 2026-09-18 12:00:00 UTC
REF_DATE = 1789732800
JOUR = 86400

# (nom, age en jours, contenu)
FICHIERS = [
    ("app.log",                    0, "recent\n"),
    ("app.log.1",                  3, "encore recent\n"),
    ("limite.log",                 7, "pile sur le seuil\n"),
    ("acces.log",                  8, "a archiver\n"),
    ("erreurs.log",               15, "a archiver aussi\n"),
    ("mon rapport final.log",     20, "espaces dans le nom\n"),
    ("rapport-2026-été.log",      12, "accents dans le nom\n"),
    ("-etrange.log",              30, "commence par un tiret\n"),
    ("vide.log",                  40, ""),
    ("gros.log",                   9, "x" * 4096),
    ("notes.txt",                 60, "pas un .log, ne bouge pas\n"),
    ("sous-dossier.log.d",        60, None),          # repertoire, pas un fichier
]

ANCIENNES_ARCHIVES = [
    "20260901-120000",
    "20260908-120000",
    "20260915-120000",
    "20260917-120000",
]


def construire(racine):
    racine = os.path.abspath(racine)
    if os.path.exists(racine):
        shutil.rmtree(racine)

    source = os.path.join(racine, "logs")
    dest = os.path.join(racine, "archives")
    os.makedirs(source)
    os.makedirs(dest)

    for nom, age, contenu in FICHIERS:
        chemin = os.path.join(source, nom)
        if contenu is None:
            os.makedirs(chemin)
            continue
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(contenu)
        quand = REF_DATE - age * JOUR
        os.utime(chemin, (quand, quand))

    # un lien symbolique vers un fichier ancien, hors de la source
    externe = os.path.join(racine, "ailleurs.log")
    with open(externe, "w", encoding="utf-8") as f:
        f.write("cible d'un lien\n")
    os.utime(externe, (REF_DATE - 50 * JOUR, REF_DATE - 50 * JOUR))
    os.symlink(externe, os.path.join(source, "lien.log"))

    for nom in ANCIENNES_ARCHIVES:
        d = os.path.join(dest, nom)
        os.makedirs(d)
        with open(os.path.join(d, "MANIFESTE.txt"), "w", encoding="utf-8") as f:
            f.write("archive: %s\n" % nom)

    return source, dest


if __name__ == "__main__":
    racine = sys.argv[1] if len(sys.argv) > 1 else "bac"
    source, dest = construire(racine)
    print("source : %s" % source)
    print("dest   : %s" % dest)
    print("REF_DATE=%d" % REF_DATE)
