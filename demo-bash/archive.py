#!/usr/bin/env python3
"""Archive les fichiers de log anciens et effectue la rotation des archives."""

import fnmatch
import os
import shutil
import sys
import time
from datetime import datetime, timezone


GARDER = 3
JOUR = 86400


def main():
    source = sys.argv[1] if len(sys.argv) > 1 else ""
    destination = sys.argv[2] if len(sys.argv) > 2 else ""
    jours = sys.argv[3] if len(sys.argv) > 3 else "7"

    if not source or not destination:
        print(f"usage: {sys.argv[0]} SOURCE DEST [JOURS]", file=sys.stderr)
        return 64

    if not os.path.isdir(source):
        print(f"source introuvable: {source}", file=sys.stderr)
        return 66

    maintenant = int(os.environ.get("REF_DATE", time.time()))
    limite = maintenant - int(jours) * JOUR
    horodatage = datetime.fromtimestamp(maintenant, timezone.utc).strftime(
        "%Y%m%d-%H%M%S"
    )
    cible = os.path.join(destination, horodatage)
    os.makedirs(cible, exist_ok=True)

    deplaces = 0
    octets = 0
    fichiers = []
    with os.scandir(source) as entrees:
        for entree in entrees:
            if entree.is_file(follow_symlinks=False) and fnmatch.fnmatchcase(
                entree.name, "*.log"
            ):
                fichiers.append(entree)

    for entree in sorted(fichiers, key=lambda item: os.fsencode(item.name)):
        mtime = entree.stat(follow_symlinks=False).st_mtime
        if mtime >= limite:
            continue
        taille = entree.stat(follow_symlinks=False).st_size
        shutil.move(entree.path, os.path.join(cible, entree.name))
        deplaces += 1
        octets += taille

    manifeste = os.path.join(cible, "MANIFESTE.txt")
    with open(manifeste, "w", encoding="utf-8") as fichier:
        fichier.write(f"archive: {horodatage}\n")
        fichier.write(f"source: {source}\n")
        fichier.write(f"limite: {limite}\n")
        fichier.write(f"fichiers: {deplaces}\n")
        fichier.write(f"octets: {octets}\n")

    archives = []
    with os.scandir(destination) as entrees:
        for entree in entrees:
            if entree.is_dir(follow_symlinks=False):
                archives.append(entree.path)
    archives.sort(key=lambda chemin: os.fsencode(os.path.basename(chemin)), reverse=True)

    supprimees = 0
    for archive in archives[GARDER:]:
        shutil.rmtree(archive)
        supprimees += 1

    print(
        f"archive={horodatage} fichiers={deplaces} "
        f"octets={octets} purgees={supprimees}"
    )
    return 1 if deplaces == 0 else 0


if __name__ == "__main__":
    sys.exit(main())