"""Calculs sur un groupe de depenses.

Toutes les sommes sont en centimes entiers. Le partage inegal (quand le
montant ne tombe pas juste) est attribue de facon deterministe : les
premiers beneficiaires par ordre alphabetique prennent le centime en plus.
"""

from collections import defaultdict


def parts(depense) -> dict[str, int]:
    """Repartit une depense entre ses beneficiaires, au centime pres."""
    n = len(depense.beneficiaires)
    base, reste = divmod(depense.montant_cents, n)
    ordre = sorted(depense.beneficiaires)
    return {p: base + (1 if i < reste else 0) for i, p in enumerate(ordre)}


def total(depenses) -> int:
    return sum(d.montant_cents for d in depenses)


def participants(depenses) -> list[str]:
    noms = set()
    for d in depenses:
        noms.add(d.paye_par)
        noms.update(d.beneficiaires)
    return sorted(noms)


def soldes(depenses) -> dict[str, int]:
    """Solde par personne : positif = on lui doit, negatif = elle doit.

    La somme des soldes vaut toujours zero.
    """
    resultat = defaultdict(int)
    for d in depenses:
        resultat[d.paye_par] += d.montant_cents
        for personne, part in parts(d).items():
            resultat[personne] -= part
    for nom in participants(depenses):
        resultat.setdefault(nom, 0)
    return dict(resultat)
