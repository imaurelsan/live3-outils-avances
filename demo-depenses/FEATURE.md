# FEATURE.md — la commande `equilibrer`

> **Ce fichier fait autorité.** En cas de contradiction avec `ENONCE.md`,
> c'est ce fichier qui gagne.

## La demande d'origine

> « À la fin du week-end, on veut savoir qui rembourse qui, avec le moins de
> virements possible. »

## Ce que ça veut dire, une fois traduit

### 1. Le calcul — `depenses/calculs.py`

```python
def transferts(depenses) -> list[tuple[str, str, int]]:
    """Rend une liste de (débiteur, créditeur, centimes)."""
```

Propriétés que la fonction doit garantir :

| Propriété | Détail |
|---|---|
| **Solde** | Après application de tous les virements, chaque solde vaut exactement 0 |
| **Centimes entiers** | Aucun flottant nulle part. La somme des virements égale la somme des dettes, au centime |
| **Borne** | **Au plus** `n-1` virements pour `n` participants — pas exactement `n-1` |
| **Déterminisme** | Deux appels sur les mêmes données rendent la **même liste, dans le même ordre** |
| **Sens** | Le débiteur paie, le créditeur reçoit. Jamais de montant négatif |

### 2. Le rendu — `depenses/rendu.py`

```python
def table_transferts(depenses) -> str:
```

Aucun calcul dans cette fonction. Groupe vide ou déjà équilibré :
`"Rien a rembourser."`

### 3. La commande — `depenses/cli.py`

```
depenses equilibrer
```

Pas d'argument. Code de retour `0`.

### 4. Les tests — `tests/`

Au moins **six** nouveaux tests, dont les cas limites ci-dessous.

## Le déterminisme, et pourquoi c'est le cœur du sujet

Un algorithme glouton apparie le plus gros débiteur avec le plus gros
créditeur. Quand deux personnes doivent le même montant, **l'ordre dans lequel
on les traite n'est pas défini** — sauf si tu le définis.

Sans règle de départage explicite, ta fonction rend parfois
`[("Ana","Cyd",500), ("Bo","Cyd",500)]` et parfois l'inverse. Ton test passe
neuf fois sur dix.

> Départage les ex aequo **par le nom**, ordre alphabétique croissant.

C'est le même piège que la date de référence du Live 2 : une source
d'indétermination cachée au fond de la logique, qui rend le test non
reproductible sans qu'on voie pourquoi.

## Les cas limites à couvrir par un test

| Cas | Attendu |
|---|---|
| Groupe vide | `[]` |
| Une seule personne qui paie pour elle-même | `[]` |
| Groupe déjà équilibré | `[]` |
| Deux personnes, 100 € payés par une pour les deux | 1 virement de 50 € |
| Trois personnes, reste non divisible | La somme des virements égale la somme des dettes, au centime |
| Deux débiteurs ex aequo | Ordre stable sur deux appels successifs |
| Un débiteur, plusieurs créditeurs | Au plus `n-1` virements |

## Ce qu'on attend d'un agent ici

C'est le premier atelier où tu le laisses toucher **quatre fichiers**. Les
règles du live s'appliquent :

1. Commit avant de lancer.
2. Une branche dédiée.
3. Périmètre borné dans le prompt : nomme les quatre fichiers, interdis le reste.
4. **Relis le diff.** S'il dépasse ce que tu peux relire, la tâche était trop grosse.
5. `pytest` après chaque couche.

Les 38 tests existants ne doivent **pas** être modifiés.

## Critères de réussite

- [ ] Les 38 tests d'origine passent, non modifiés
- [ ] Au moins 6 nouveaux tests, dont les 7 cas limites
- [ ] Les soldes retombent tous à zéro après application des virements
- [ ] Aucun flottant dans le calcul
- [ ] Deux appels successifs rendent la même liste
- [ ] `depenses equilibrer` fonctionne et rend `0`

## Lancer

```bash
pip install pytest
pytest -q
python3 -m depenses.cli --fichier exemple.json soldes
```
