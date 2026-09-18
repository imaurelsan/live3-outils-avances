"""Modele de donnees."""

from dataclasses import dataclass, field


class ErreurValidation(ValueError):
    """Une donnee fournie par l'appelant est invalide."""


LIBELLE_MAX = 120


@dataclass(frozen=True)
class Depense:
    id: int
    libelle: str
    montant_cents: int
    paye_par: str
    beneficiaires: tuple[str, ...]

    def en_dict(self) -> dict:
        return {
            "id": self.id,
            "libelle": self.libelle,
            "montant_cents": self.montant_cents,
            "paye_par": self.paye_par,
            "beneficiaires": list(self.beneficiaires),
        }


def valider_libelle(valeur) -> str:
    if not isinstance(valeur, str):
        raise ErreurValidation("le libelle doit etre une chaine")
    propre = valeur.strip()
    if not propre:
        raise ErreurValidation("le libelle ne peut pas etre vide")
    if len(propre) > LIBELLE_MAX:
        raise ErreurValidation("le libelle depasse %d caracteres" % LIBELLE_MAX)
    return propre


def valider_montant(valeur) -> int:
    """Les montants sont en centimes entiers. Jamais de flottant ici."""
    if isinstance(valeur, bool) or not isinstance(valeur, int):
        raise ErreurValidation("le montant doit etre un entier de centimes")
    if valeur <= 0:
        raise ErreurValidation("le montant doit etre strictement positif")
    return valeur


def valider_personne(valeur) -> str:
    if not isinstance(valeur, str):
        raise ErreurValidation("un nom doit etre une chaine")
    propre = valeur.strip()
    if not propre:
        raise ErreurValidation("un nom ne peut pas etre vide")
    return propre


def valider_beneficiaires(valeur) -> tuple[str, ...]:
    if not isinstance(valeur, (list, tuple)):
        raise ErreurValidation("les beneficiaires doivent etre une liste")
    propres = []
    for p in valeur:
        nom = valider_personne(p)
        if nom not in propres:
            propres.append(nom)
    if not propres:
        raise ErreurValidation("il faut au moins un beneficiaire")
    return tuple(propres)
