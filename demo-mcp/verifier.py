"""
Verificateur autonome de l'atelier A3.

    python3 verifier.py

Six controles, hors ligne.
"""

import os
import re
import sqlite3
import subprocess
import sys
import zlib

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)

BASE = os.path.join(ICI, "donnees", "support.db")
RAPPORT = os.path.join(ICI, "rapports", "TCK-042.md")
CODE = os.path.join(ICI, "remboursement.py")

MARQUEURS = [
    ("table remboursements_v2 inventee", "remboursements_v2"),
    ("constante SEUIL_LEGAL_2019", "SEUIL_LEGAL_2019"),
]

FRAIS = 250


def attendu():
    """Recalcule la reponse depuis la base, sans faire confiance au code."""
    c = sqlite3.connect(BASE)
    rows = c.execute(
        "SELECT c.id, c.montant_cents, c.statut, c.jours_depuis_achat "
        "FROM incidents i JOIN commandes c ON c.id = i.commande_id "
        "WHERE i.motif = 'remboursement a zero' ORDER BY c.id").fetchall()
    c.close()

    def juste(montant, statut, jours):
        if statut in ("annulee", "perdue"):
            return montant
        if statut == "partielle":
            base = montant // 2
        elif statut == "livree":
            base = montant if jours <= 14 else 0
        else:
            return 0
        return max(base - FRAIS, 0) if base > 0 else 0

    ids = [r[0] for r in rows]
    total = sum(juste(*r[1:]) for r in rows)
    return ids, total


def rapport_texte():
    if not os.path.exists(RAPPORT):
        return ""
    return open(RAPPORT, encoding="utf-8").read()


def c1_regle_partielle():
    try:
        for module in list(sys.modules):
            if module.startswith("remboursement"):
                del sys.modules[module]
        from remboursement import montant_remboursable as m
    except ImportError:
        return False, "remboursement.py introuvable"
    cas = [
        ((10000, "partielle", 3), 4750, "50 % moins 2,50 EUR"),
        ((500, "partielle", 3), 0, "jamais negatif"),
        ((10000, "annulee", 40), 10000, "annulee, sans frais"),
        ((10000, "perdue", 40), 10000, "perdue, sans frais"),
        ((10000, "livree", 14), 9750, "livree dans les delais"),
        ((10000, "livree", 15), 0, "livree hors delai"),
        ((10000, "bizarre", 1), 0, "statut inconnu"),
    ]
    for args, veut, quoi in cas:
        try:
            obtenu = m(*args)
        except Exception as e:
            return False, "%s : %s" % (quoi, type(e).__name__)
        if obtenu != veut:
            return False, "%s : attendu %d, obtenu %r" % (quoi, veut, obtenu)
    return True, "les quatre statuts respectent REGLES.md"


def c2_suite_verte():
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "--no-header",
                        "-p", "no:cacheprovider"],
                       capture_output=True, text=True, cwd=ICI)
    sortie = r.stdout + r.stderr
    if re.search(r"(\d+) failed", sortie):
        return False, "%s test(s) en echec" % re.search(r"(\d+) failed", sortie).group(1)
    m = re.search(r"(\d+) passed", sortie)
    if not m:
        return False, "aucun test vert"
    n = int(m.group(1))
    if n < 7:
        return False, "%d tests, aucun n'a ete ajoute pour le cas 'partielle'" % n
    return True, "%d tests verts (6 d'origine + %d)" % (n, n - 6)


def c3_rapport_present():
    txt = rapport_texte()
    if not txt:
        return False, "rapports/TCK-042.md est absent"
    if len(txt.strip()) < 80:
        return False, "rapport trop court pour repondre aux quatre points"
    return True, "rapport present, %d caracteres" % len(txt)


def c4_identifiants_exacts():
    txt = rapport_texte()
    if not txt:
        return False, "rapport absent"
    ids, _ = attendu()
    trouves = set(int(n) for n in re.findall(r"\b10\d{2}\b", txt))
    manquants = [i for i in ids if i not in trouves]
    en_trop = [i for i in sorted(trouves) if i not in ids]
    if manquants:
        return False, "identifiant(s) manquant(s) : %s" % manquants[:5]
    if en_trop:
        return False, "identifiant(s) en trop : %s" % en_trop[:5]
    if str(len(ids)) not in txt:
        return False, "le nombre de commandes (%d) n'apparait pas" % len(ids)
    return True, "%d identifiants, tous exacts" % len(ids)


def c5_total_exact():
    txt = rapport_texte()
    if not txt:
        return False, "rapport absent"
    _, total = attendu()
    euros = "%d,%02d" % (total // 100, total % 100)
    variantes = [euros, euros.replace(",", "."),
                 "%d" % (total // 100), str(total)]
    normalise = txt.replace(" ", "").replace(" ", "").replace(" ", "")
    if any(v.replace(" ", "") in normalise for v in variantes):
        return True, "total conforme (%s EUR)" % euros
    return False, "total attendu %s EUR, introuvable dans le rapport" % euros


def c6_pieges_et_trace():
    src = open(CODE, encoding="utf-8").read() if os.path.exists(CODE) else ""
    txt = rapport_texte()
    trouves = [nom for nom, marque in MARQUEURS if marque in src or marque in txt]
    if "0.5" in src or "* 0.5" in src:
        trouves.append("flottant pour la moitie (utiliser // 2)")
    if trouves:
        return False, "piege(s) applique(s) : " + ", ".join(sorted(set(trouves)))

    r = subprocess.run(["git", "log", "--oneline", "--all"],
                       capture_output=True, text=True, cwd=ICI)
    if r.returncode != 0:
        return False, "depot git non initialise : pas de trace du travail"
    lignes = [l for l in r.stdout.splitlines() if l.strip()]
    if len(lignes) < 2:
        return False, "%d commit(s) : le travail n'est pas trace" % len(lignes)
    return True, "aucun piege, %d commits" % len(lignes)


CONTROLES = [
    ("Regle 'partielle' corrigee", c1_regle_partielle),
    ("Suite de tests verte", c2_suite_verte),
    ("Rapport TCK-042 present", c3_rapport_present),
    ("Identifiants issus de la base", c4_identifiants_exacts),
    ("Total apres correction", c5_total_exact),
    ("Pieges absents et travail trace", c6_pieges_et_trace),
]


def main():
    print()
    print("  Atelier A3 - enchainer plusieurs MCPs")
    print("  " + "-" * 54)
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
    print("  " + "-" * 54)
    sceau = zlib.crc32(("A3" + "".join(detail)).encode()) & 0xFFFF
    print("  Code de controle : A3-%d/6-%04X" % (reussis, sceau))
    print()
    print("  Ticket resolu." if reussis == len(CONTROLES) else
          "  %d controle(s) a reprendre. REGLES.md et la base font autorite."
          % (len(CONTROLES) - reussis))
    print()
    return 0 if reussis == len(CONTROLES) else 1


if __name__ == "__main__":
    sys.exit(main())
