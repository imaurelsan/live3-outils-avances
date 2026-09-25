import pytest

from remboursement import montant_remboursable as m


def test_annulee_integrale():
    assert m(10000, "annulee", 3) == 10000


def test_perdue_integrale():
    assert m(10000, "perdue", 40) == 10000


def test_partielle_moitie_moins_frais():
    assert m(10000, "partielle", 3) == 4750


def test_livree_dans_les_delais():
    assert m(10000, "livree", 14) == 10000 - 250


def test_livree_hors_delai():
    assert m(10000, "livree", 15) == 0


def test_jamais_negatif():
    assert m(100, "livree", 1) == 0


def test_statut_inconnu_rend_zero():
    assert m(10000, "bizarre", 1) == 0
