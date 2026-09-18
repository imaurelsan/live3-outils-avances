"""
Calcul des remboursements clients.

Regles metier : voir REGLES.md.
"""

TAUX_TVA = 0.20
FRAIS_DOSSIER_CENTS = 250


class StatutInconnu(ValueError):
    pass


def montant_remboursable(montant_cents, statut, jours_depuis_achat):
    """Part remboursable d'une commande, en centimes.

    statut : 'livree', 'partielle', 'annulee', 'perdue'
    """
    if statut == "annulee":
        base = montant_cents
    elif statut == "perdue":
        base = montant_cents
    elif statut == "livree":
        base = montant_cents if jours_depuis_achat <= 14 else 0
    else:
        base = 0

    if base <= 0:
        return 0
    if statut in ("annulee", "perdue"):
        return base
    return max(base - FRAIS_DOSSIER_CENTS, 0)


def rembourser(commande):
    """commande : dict issu de la base support."""
    return montant_remboursable(
        commande["montant_cents"],
        commande["statut"],
        commande["jours_depuis_achat"],
    )
