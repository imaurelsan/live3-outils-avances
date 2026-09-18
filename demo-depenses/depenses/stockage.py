"""Persistance JSON."""

import json
import os

from .modeles import (
    Depense,
    valider_beneficiaires,
    valider_libelle,
    valider_montant,
    valider_personne,
)


class Groupe:
    def __init__(self):
        self._depenses: list[Depense] = []
        self._prochain_id = 1

    def ajouter(self, libelle, montant_cents, paye_par, beneficiaires) -> Depense:
        d = Depense(
            id=self._prochain_id,
            libelle=valider_libelle(libelle),
            montant_cents=valider_montant(montant_cents),
            paye_par=valider_personne(paye_par),
            beneficiaires=valider_beneficiaires(beneficiaires),
        )
        self._depenses.append(d)
        self._prochain_id += 1
        return d

    def supprimer(self, id_depense) -> None:
        avant = len(self._depenses)
        self._depenses = [d for d in self._depenses if d.id != id_depense]
        if len(self._depenses) == avant:
            raise LookupError("aucune depense d'identifiant %s" % id_depense)

    def lister(self) -> list[Depense]:
        return list(self._depenses)

    def __len__(self) -> int:
        return len(self._depenses)

    # --- persistance ----------------------------------------------------

    def en_dict(self) -> dict:
        return {"prochain_id": self._prochain_id,
                "depenses": [d.en_dict() for d in self._depenses]}

    @classmethod
    def depuis_dict(cls, brut) -> "Groupe":
        g = cls()
        g._prochain_id = brut.get("prochain_id", 1)
        for d in brut.get("depenses", []):
            g._depenses.append(Depense(
                id=d["id"],
                libelle=d["libelle"],
                montant_cents=d["montant_cents"],
                paye_par=d["paye_par"],
                beneficiaires=tuple(d["beneficiaires"]),
            ))
        return g


def charger(chemin) -> Groupe:
    if not os.path.exists(chemin):
        return Groupe()
    with open(chemin, encoding="utf-8") as f:
        return Groupe.depuis_dict(json.load(f))


def sauver(groupe, chemin) -> None:
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(groupe.en_dict(), f, ensure_ascii=False, indent=2)
        f.write("\n")
