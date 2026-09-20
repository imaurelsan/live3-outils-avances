import json

import pytest

from depenses import Groupe, ErreurValidation, charger, parts, sauver, soldes, total
from depenses.calculs import transferts
from depenses.cli import euros_vers_cents, main
from depenses.rendu import euros, table_transferts


@pytest.fixture
def groupe():
    g = Groupe()
    g.ajouter("Courses", 6000, "Ana", ["Ana", "Bo", "Cyd"])
    g.ajouter("Essence", 4500, "Bo", ["Ana", "Bo"])
    return g


# --- modele -------------------------------------------------------------

def test_ajouter(groupe):
    assert len(groupe) == 2
    assert groupe.lister()[0].id == 1


@pytest.mark.parametrize("montant", [0, -100, 12.5, "10", True])
def test_montant_invalide(montant):
    with pytest.raises(ErreurValidation):
        Groupe().ajouter("X", montant, "Ana", ["Ana"])


@pytest.mark.parametrize("libelle", ["", "   ", None, "x" * 121])
def test_libelle_invalide(libelle):
    with pytest.raises(ErreurValidation):
        Groupe().ajouter(libelle, 100, "Ana", ["Ana"])


def test_beneficiaires_vides():
    with pytest.raises(ErreurValidation):
        Groupe().ajouter("X", 100, "Ana", [])


def test_beneficiaires_dedupliques():
    d = Groupe().ajouter("X", 100, "Ana", ["Ana", "Ana", "Bo"])
    assert d.beneficiaires == ("Ana", "Bo")


def test_supprimer_inconnu(groupe):
    with pytest.raises(LookupError):
        groupe.supprimer(404)


# --- calculs ------------------------------------------------------------

def test_parts_exactes(groupe):
    assert parts(groupe.lister()[0]) == {"Ana": 2000, "Bo": 2000, "Cyd": 2000}


def test_parts_avec_reste():
    """100 centimes pour 3 : le reste va aux premiers dans l'ordre alpha."""
    d = Groupe().ajouter("X", 100, "Ana", ["Cyd", "Ana", "Bo"])
    assert parts(d) == {"Ana": 34, "Bo": 33, "Cyd": 33}
    assert sum(parts(d).values()) == 100


def test_total(groupe):
    assert total(groupe.lister()) == 10500


def test_soldes_somment_a_zero(groupe):
    assert sum(soldes(groupe.lister()).values()) == 0


def test_soldes_valeurs(groupe):
    s = soldes(groupe.lister())
    assert s == {"Ana": 6000 - 2000 - 2250, "Bo": 4500 - 2000 - 2250, "Cyd": -2000}


def test_soldes_groupe_vide():
    assert soldes([]) == {}


# --- rendu --------------------------------------------------------------

@pytest.mark.parametrize("cents,attendu", [
    (0, "0,00 EUR"), (5, "0,05 EUR"), (4250, "42,50 EUR"), (-1750, "-17,50 EUR"),
])
def test_euros(cents, attendu):
    assert euros(cents) == attendu


# --- cli ----------------------------------------------------------------

@pytest.mark.parametrize("texte,cents", [
    ("42.50", 4250), ("42,50", 4250), ("7", 700), ("0.05", 5), ("12.5", 1250),
])
def test_euros_vers_cents(texte, cents):
    assert euros_vers_cents(texte) == cents


@pytest.mark.parametrize("texte", ["abc", "", "4.2.1", "-5"])
def test_euros_vers_cents_invalide(texte):
    with pytest.raises(ErreurValidation):
        euros_vers_cents(texte)


def test_cli_ajouter_et_lister(tmp_path, capsys):
    f = str(tmp_path / "g.json")
    assert main(["--fichier", f, "ajouter", "Pizza", "30.00",
                 "--par", "Ana", "--pour", "Ana", "Bo"]) == 0
    assert main(["--fichier", f, "lister"]) == 0
    assert "Pizza" in capsys.readouterr().out


def test_cli_montant_invalide(tmp_path):
    f = str(tmp_path / "g.json")
    assert main(["--fichier", f, "ajouter", "X", "abc",
                 "--par", "Ana", "--pour", "Ana"]) == 2


def test_cli_supprimer_inconnu(tmp_path):
    f = str(tmp_path / "g.json")
    assert main(["--fichier", f, "supprimer", "404"]) == 3


# --- persistance --------------------------------------------------------

def test_aller_retour_json(groupe, tmp_path):
    f = str(tmp_path / "g.json")
    sauver(groupe, f)
    relu = charger(f)
    assert [d.en_dict() for d in relu.lister()] == \
           [d.en_dict() for d in groupe.lister()]


def test_charger_fichier_absent(tmp_path):
    assert len(charger(str(tmp_path / "absent.json"))) == 0


def test_json_serialisable(groupe, tmp_path):
    f = str(tmp_path / "g.json")
    sauver(groupe, f)
    json.loads(open(f, encoding="utf-8").read())


# --- transferts ---------------------------------------------------------

def test_transferts_groupe_vide():
    assert transferts([]) == []


def test_transferts_une_personne_paie_pour_elle_meme():
    d = Groupe().ajouter("X", 1000, "Ana", ["Ana"])
    assert transferts([d]) == []


def test_transferts_groupe_deja_equilibre():
    g = Groupe()
    g.ajouter("X", 1000, "Ana", ["Ana", "Bo"])
    g.ajouter("Y", 1000, "Bo", ["Ana", "Bo"])
    assert transferts(g.lister()) == []
    assert table_transferts(g.lister()) == "Rien a rembourser."


def test_transferts_deux_personnes():
    d = Groupe().ajouter("X", 10000, "Ana", ["Ana", "Bo"])
    assert transferts([d]) == [("Bo", "Ana", 5000)]


def test_transferts_reste_non_divisible():
    d = Groupe().ajouter("X", 100, "Ana", ["Ana", "Bo", "Cyd"])
    virements = transferts([d])
    assert sum(montant for _, _, montant in virements) == 66
    assert all(isinstance(montant, int) and montant > 0
               for _, _, montant in virements)


def test_transferts_debiteurs_ex_aequo_deterministes():
    d = Groupe().ajouter("A", 3000, "Ana", ["Ana", "Bo", "Cyd"])
    virements = transferts([d])
    assert virements == transferts([d])
    assert [debiteur for debiteur, _, _ in virements] == ["Bo", "Cyd"]


def test_transferts_un_debiteur_plusieurs_crediteurs():
    g = Groupe()
    g.ajouter("A", 1000, "Ana", ["Ana", "Bo"])
    g.ajouter("B", 1000, "Cyd", ["Cyd", "Bo"])
    virements = transferts(g.lister())
    assert len(virements) <= 2
    assert {crediteur for _, crediteur, _ in virements} == {"Ana", "Cyd"}


def test_cli_equilibrer_retourne_zero(tmp_path, capsys):
    f = str(tmp_path / "g.json")
    assert main(["--fichier", f, "equilibrer"]) == 0
    assert capsys.readouterr().out.strip() == "Rien a rembourser."
