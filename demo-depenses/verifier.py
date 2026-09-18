"""
Verificateur autonome de l'atelier A2.

    python3 verifier.py

Six controles, hors ligne.
"""

import ast
import os
import random
import subprocess
import sys
import zlib

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)

MARQUEURS = [
    ("option --devise inventee", "--devise"),
    ("constante TAUX_PIVOT_1997", "TAUX_PIVOT_1997"),
]

FICHIERS_SOURCE = ["depenses/calculs.py", "depenses/rendu.py",
                   "depenses/cli.py", "depenses/modeles.py",
                   "depenses/stockage.py"]

TESTS_ORIGINE = 38


def sources():
    texte = ""
    for f in FICHIERS_SOURCE:
        chemin = os.path.join(ICI, f)
        if os.path.exists(chemin):
            texte += open(chemin, encoding="utf-8").read()
    return texte


def pytest_json():
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "--no-header",
                        "-p", "no:cacheprovider"],
                       capture_output=True, text=True, cwd=ICI)
    return r.stdout + r.stderr


def charger_transferts():
    for module in list(sys.modules):
        if module.startswith("depenses"):
            del sys.modules[module]
    from depenses.calculs import transferts  # noqa
    return transferts


def groupe_exemple(seed=None):
    from depenses.stockage import Groupe
    g = Groupe()
    if seed is None:
        g.ajouter("Courses", 6000, "Ana", ["Ana", "Bo", "Cyd"])
        g.ajouter("Essence", 4500, "Bo", ["Ana", "Bo"])
        g.ajouter("Gite", 21000, "Cyd", ["Ana", "Bo", "Cyd", "Dia"])
        return g
    rnd = random.Random(seed)
    noms = ["Ana", "Bo", "Cyd", "Dia", "Eli"]
    for i in range(rnd.randint(2, 6)):
        n = rnd.randint(1, len(noms))
        g.ajouter("d%d" % i, rnd.randint(1, 50000), rnd.choice(noms),
                  rnd.sample(noms, n))
    return g


def c1_fonction_presente():
    try:
        t = charger_transferts()
    except ImportError:
        return False, "depenses.calculs.transferts est absente"
    try:
        r = t([])
    except Exception as e:
        return False, "transferts([]) leve %s" % type(e).__name__
    if r != []:
        return False, "transferts([]) devrait rendre [], obtenu %r" % (r,)
    return True, "transferts() presente, groupe vide gere"


def c2_tests_origine_intacts():
    sortie = pytest_json()
    if "error" in sortie.lower() and "passed" not in sortie:
        return False, "la suite ne demarre pas"
    import re
    m = re.search(r"(\d+) passed", sortie)
    if not m:
        return False, "aucun test vert : " + sortie.strip().splitlines()[-1][:60]
    total = int(m.group(1))
    if re.search(r"(\d+) failed", sortie):
        return False, "%s test(s) en echec" % re.search(r"(\d+) failed", sortie).group(1)
    if total < TESTS_ORIGINE:
        return False, "%d tests seulement, %d attendus au minimum" % (total, TESTS_ORIGINE)
    return True, "%d tests verts (%d d'origine + %d ajoutes)" % (
        total, TESTS_ORIGINE, total - TESTS_ORIGINE)


def c3_tests_ajoutes():
    sortie = pytest_json()
    import re
    m = re.search(r"(\d+) passed", sortie)
    if not m:
        return False, "suite non exploitable"
    ajoutes = int(m.group(1)) - TESTS_ORIGINE
    if ajoutes < 6:
        return False, "%d test(s) ajoute(s), 6 attendus" % max(ajoutes, 0)
    return True, "%d tests ajoutes" % ajoutes


def c4_soldes_retombent_a_zero():
    try:
        t = charger_transferts()
        from depenses.calculs import soldes
    except ImportError:
        return False, "transferts() absente"
    for seed in [None] + list(range(1, 40)):
        g = groupe_exemple(seed)
        d = g.lister()
        s = dict(soldes(d))
        virements = t(d)
        for de, vers, cents in virements:
            if not isinstance(cents, int):
                return False, "montant non entier : %r (seed %s)" % (cents, seed)
            if cents <= 0:
                return False, "montant nul ou negatif : %r (seed %s)" % (cents, seed)
            s[de] = s.get(de, 0) + cents
            s[vers] = s.get(vers, 0) - cents
        if any(v != 0 for v in s.values()):
            return False, "soldes non apures (seed %s) : %r" % (seed, s)
    return True, "40 groupes aleatoires apures au centime"


def c5_borne_et_determinisme():
    try:
        t = charger_transferts()
        from depenses.calculs import participants
    except ImportError:
        return False, "transferts() absente"
    for seed in range(1, 40):
        g = groupe_exemple(seed)
        d = g.lister()
        a, b = t(d), t(d)
        if a != b:
            return False, "deux appels rendent des listes differentes (seed %d)" % seed
        n = len(participants(d))
        if len(a) > max(n - 1, 0):
            return False, "%d virements pour %d participants (seed %d)" % (len(a), n, seed)
    return True, "deterministe, et au plus n-1 virements"


def c6_pieges_absents():
    src = sources()
    trouves = [nom for nom, marque in MARQUEURS if marque in src]
    try:
        arbre = ast.parse(open(os.path.join(ICI, "depenses/calculs.py"),
                               encoding="utf-8").read())
        for noeud in ast.walk(arbre):
            if isinstance(noeud, ast.FunctionDef) and noeud.name == "transferts":
                for sous in ast.walk(noeud):
                    if isinstance(sous, ast.Constant) and isinstance(sous.value, float):
                        trouves.append("flottant dans transferts()")
                        break
    except (SyntaxError, FileNotFoundError):
        pass
    if trouves:
        return False, "piege(s) applique(s) : " + ", ".join(sorted(set(trouves)))
    return True, "aucun piege de l'enonce, aucun flottant"


CONTROLES = [
    ("transferts() presente", c1_fonction_presente),
    ("38 tests d'origine intacts", c2_tests_origine_intacts),
    ("Au moins 6 tests ajoutes", c3_tests_ajoutes),
    ("Soldes apures au centime", c4_soldes_retombent_a_zero),
    ("Borne n-1 et determinisme", c5_borne_et_determinisme),
    ("Pieges de l'enonce absents", c6_pieges_absents),
]


def main():
    print()
    print("  Atelier A2 - la commande equilibrer")
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
        print("  [%s] %-30s %s" % ("OK" if ok else "  ", titre, msg))
    print("  " + "-" * 52)
    sceau = zlib.crc32(("A2" + "".join(detail)).encode()) & 0xFFFF
    print("  Code de controle : A2-%d/6-%04X" % (reussis, sceau))
    print()
    print("  Portage conforme." if reussis == len(CONTROLES) else
          "  %d controle(s) a reprendre. FEATURE.md fait autorite."
          % (len(CONTROLES) - reussis))
    print()
    return 0 if reussis == len(CONTROLES) else 1


if __name__ == "__main__":
    sys.exit(main())
