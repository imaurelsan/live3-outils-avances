"""
Verificateur autonome de l'atelier A1.

    python3 verifier.py

Six controles, hors ligne. Il compare le comportement de ton portage a
celui du script bash d'origine, sur la meme fixture.
"""

import os
import re
import subprocess
import sys
import zlib

ICI = os.path.dirname(os.path.abspath(__file__))
PORT = os.path.join(ICI, "archive.py")
REF = "1789732800"

# Chaines qui ne doivent PAS se retrouver dans le portage : ce sont les
# pieges de l'enonce, appliques tels quels.
MARQUEURS = [
    ("option --turbo inventee", "--turbo"),
    ("constante SEUIL_QUALITE_9001", "SEUIL_QUALITE_9001"),
]


def run(cmd, **kw):
    return subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True,
                          text=True, cwd=ICI, **kw)


def capture(commande):
    """Rejoue golden.sh sur la commande donnee."""
    r = run(["bash", os.path.join(ICI, "golden.sh"), commande])
    return r.stdout


def c1_portage_present():
    if not os.path.exists(PORT):
        return False, "archive.py est absent"
    src = open(PORT, encoding="utf-8").read()
    if len(src.strip()) < 200:
        return False, "archive.py semble vide"
    if "subprocess" in src and "archive.sh" in src:
        return False, "archive.py appelle le script bash au lieu de le porter"
    return True, "archive.py present, %d lignes" % len(src.splitlines())


def c2_comportement_identique():
    attendu = os.path.join(ICI, "golden.txt")
    if not os.path.exists(attendu):
        return False, "golden.txt absent, relance ./golden.sh ./archive.sh > golden.txt"
    ref = open(attendu, encoding="utf-8").read()
    obtenu = capture("python3 " + PORT)
    if not obtenu.strip():
        return False, "le portage n'a rien produit"
    if obtenu == ref:
        return True, "sortie, arbre et manifeste identiques"
    # diagnostic par section
    def bloc(txt, nom):
        m = re.search(r"=== %s ===\n(.*?)(?=\n=== |\Z)" % nom, txt, re.S)
        return m.group(1) if m else ""
    ecarts = [n for n in ("SORTIE", "CODE", "ARBRE", "MANIFESTE", "CAS LIMITES")
              if bloc(ref, n) != bloc(obtenu, n)]
    return False, "ecart sur : " + ", ".join(ecarts)


def c3_codes_de_sortie():
    obtenu = capture("python3 " + PORT)
    m = re.search(r"=== CAS LIMITES ===\n(.*)", obtenu, re.S)
    if not m:
        return False, "cas limites non joues"
    bloc = m.group(1)
    attendus = {"manquant": "66", "vide": "1", "sans-argument": "64"}
    faux = []
    for cle, val in attendus.items():
        trouve = re.search(r"%s -> (\d+)" % re.escape(cle), bloc)
        if not trouve or trouve.group(1) != val:
            faux.append("%s attendu %s, obtenu %s" %
                        (cle, val, trouve.group(1) if trouve else "rien"))
    if faux:
        return False, " ; ".join(faux)
    return True, "64, 66, 1 et 0 respectes"


def c4_noms_exotiques():
    obtenu = capture("python3 " + PORT)
    m = re.search(r"=== ARBRE ===\n(.*?)\n=== ", obtenu, re.S)
    if not m:
        return False, "arbre non produit"
    arbre = m.group(1)
    manquants = [n for n in ("mon rapport final.log", "rapport-2026-été.log",
                             "-etrange.log", "vide.log")
                 if ("archives/20260918-120000/" + n) not in arbre]
    if manquants:
        return False, "non archive(s) : " + ", ".join(manquants)
    return True, "espaces, accents, tiret initial et fichier vide traites"


def c5_symlinks_et_dossiers():
    if not os.path.exists(PORT):
        return False, "archive.py absent"
    obtenu = capture("python3 " + PORT)
    m = re.search(r"=== ARBRE ===\n(.*?)\n=== ", obtenu, re.S)
    if not m:
        return False, "arbre non produit"
    arbre = m.group(1)
    fautes = []
    if "./logs/lien.log" not in arbre:
        fautes.append("le lien symbolique a ete deplace")
    if "./logs/sous-dossier.log.d" not in arbre:
        fautes.append("un repertoire a ete deplace")
    if "./logs/notes.txt" not in arbre:
        fautes.append("un fichier hors motif *.log a ete deplace")
    if "./logs/limite.log" not in arbre:
        fautes.append("le fichier pile sur le seuil a ete archive (le bash le garde)")
    if fautes:
        return False, " ; ".join(fautes)
    return True, "lien, repertoire, hors-motif et seuil exact respectes"


def c6_pieges_absents():
    if not os.path.exists(PORT):
        return False, "archive.py absent"
    src = open(PORT, encoding="utf-8").read()
    trouves = [nom for nom, marque in MARQUEURS if marque in src]
    if trouves:
        return False, "piege(s) de l'enonce applique(s) : " + ", ".join(trouves)
    return True, "aucun piege de l'enonce dans le code"


CONTROLES = [
    ("Portage present et autonome", c1_portage_present),
    ("Comportement identique au bash", c2_comportement_identique),
    ("Codes de sortie", c3_codes_de_sortie),
    ("Noms de fichiers exotiques", c4_noms_exotiques),
    ("Liens, repertoires, seuil exact", c5_symlinks_et_dossiers),
    ("Pieges de l'enonce absents", c6_pieges_absents),
]


def main():
    print()
    print("  Atelier A1 - portage de archive.sh")
    print("  " + "-" * 52)
    reussis = 0
    detail = []
    for titre, fn in CONTROLES:
        try:
            ok, msg = fn()
        except Exception as e:
            ok, msg = False, "erreur du controle : %s" % e
        reussis += 1 if ok else 0
        detail.append("1" if ok else "0")
        print("  [%s] %-32s %s" % ("OK" if ok else "  ", titre, msg))
    print("  " + "-" * 52)
    sceau = zlib.crc32(("A1" + "".join(detail)).encode()) & 0xFFFF
    print("  Code de controle : A1-%d/6-%04X" % (reussis, sceau))
    print()
    if reussis < len(CONTROLES):
        print("  %d controle(s) a reprendre. Le bash fait autorite." %
              (len(CONTROLES) - reussis))
    else:
        print("  Portage conforme.")
    print()
    return 0 if reussis == len(CONTROLES) else 1


if __name__ == "__main__":
    sys.exit(main())
