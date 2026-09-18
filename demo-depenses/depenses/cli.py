"""Interface en ligne de commande."""

import argparse
import sys

from .calculs import total
from .modeles import ErreurValidation
from .rendu import euros, table_depenses, table_soldes
from .stockage import charger, sauver

FICHIER_DEFAUT = "groupe.json"


def construire_parseur():
    p = argparse.ArgumentParser(prog="depenses",
                                description="Depenses partagees d'un groupe.")
    p.add_argument("--fichier", default=FICHIER_DEFAUT,
                   help="fichier de donnees (defaut: %s)" % FICHIER_DEFAUT)
    sp = p.add_subparsers(dest="commande", required=True)

    a = sp.add_parser("ajouter", help="ajoute une depense")
    a.add_argument("libelle")
    a.add_argument("montant", help="en euros, ex: 42.50")
    a.add_argument("--par", required=True, help="qui a paye")
    a.add_argument("--pour", required=True, nargs="+", help="beneficiaires")

    sp.add_parser("lister", help="liste les depenses")
    sp.add_parser("total", help="affiche le total")
    sp.add_parser("soldes", help="affiche le solde de chacun")

    s = sp.add_parser("supprimer", help="supprime une depense")
    s.add_argument("id", type=int)
    return p


def euros_vers_cents(texte) -> int:
    """« 42.50 » ou « 42,50 » -> 4250. Pas de flottant intermediaire."""
    t = str(texte).strip().replace(",", ".")
    if "." not in t:
        entier, decimales = t, "00"
    else:
        entier, _, decimales = t.partition(".")
    if not entier.isdigit() or not decimales.isdigit():
        raise ErreurValidation("montant illisible : %s" % texte)
    decimales = (decimales + "00")[:2]
    return int(entier) * 100 + int(decimales)


def main(argv=None):
    args = construire_parseur().parse_args(argv)
    groupe = charger(args.fichier)

    try:
        if args.commande == "ajouter":
            d = groupe.ajouter(args.libelle, euros_vers_cents(args.montant),
                               args.par, args.pour)
            sauver(groupe, args.fichier)
            print("ajoute #%d : %s %s" % (d.id, d.libelle, euros(d.montant_cents)))
        elif args.commande == "lister":
            print(table_depenses(groupe.lister()))
        elif args.commande == "total":
            print(euros(total(groupe.lister())))
        elif args.commande == "soldes":
            print(table_soldes(groupe.lister()))
        elif args.commande == "supprimer":
            groupe.supprimer(args.id)
            sauver(groupe, args.fichier)
            print("supprime #%d" % args.id)
    except ErreurValidation as e:
        print("erreur : %s" % e, file=sys.stderr)
        return 2
    except LookupError as e:
        print("erreur : %s" % e, file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
