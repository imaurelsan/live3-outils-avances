"""Rendu texte. Aucune logique de calcul ici."""

from .calculs import soldes, total, transferts


def euros(cents: int) -> str:
    """Formate des centimes en euros. Gere le signe correctement."""
    signe = "-" if cents < 0 else ""
    c = abs(cents)
    return "%s%d,%02d EUR" % (signe, c // 100, c % 100)


def table_depenses(depenses) -> str:
    if not depenses:
        return "Aucune depense."
    lignes = ["%-4s %-28s %12s %-10s %s" % ("ID", "LIBELLE", "MONTANT", "PAYE PAR", "POUR"),
              "-" * 78]
    for d in depenses:
        lignes.append("%-4d %-28s %12s %-10s %s" % (
            d.id, d.libelle[:28], euros(d.montant_cents), d.paye_par,
            ", ".join(sorted(d.beneficiaires))))
    lignes.append("-" * 78)
    lignes.append("%-4s %-28s %12s" % ("", "TOTAL", euros(total(depenses))))
    return "\n".join(lignes)


def table_soldes(depenses) -> str:
    s = soldes(depenses)
    if not s:
        return "Aucune depense."
    lignes = ["%-14s %12s" % ("PERSONNE", "SOLDE"), "-" * 27]
    for nom in sorted(s):
        lignes.append("%-14s %12s" % (nom, euros(s[nom])))
    return "\n".join(lignes)


def table_transferts(depenses) -> str:
    virements = transferts(depenses)
    if not virements:
        return "Rien a rembourser."
    lignes = ["DEBITEUR       CREDITEUR          MONTANT", "-" * 44]
    for debiteur, crediteur, montant in virements:
        lignes.append("%-14s %-18s %12s" % (
            debiteur, crediteur, euros(montant)))
    return "\n".join(lignes)
